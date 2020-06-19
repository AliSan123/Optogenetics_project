#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 14:58:21 2020
@author: peter
"""
import os
os.getcwd()
os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox')


import numpy as np
import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import scipy.stats
import pandas as pd

def load_ephys(path,lazy = False):
    reader = neo.io.Spike2IO(path)
    bl = reader.read(lazy = lazy)[0]
    return bl

#file in dropbox
ephys_fname = 'Cell4TCourse.smr'
calibration_fname = 'power_calibration_980nm_8um_spot.dat'

#load using python-neo
ephys = load_ephys(ephys_fname)

#   AS - Eplore ephys
# ephys.segments[0] # Only contains 1 segment with 3 chennels:
#                   #  0: AnalogSignal with 2 channels of length 3411957; units V; datatype float32 
#                   #  1: AnalogSignal with 2 channels of length 13647828; units mV; datatype float32
#                   #  2: AnalogSignal with 2 channels of length 13647828; units nA; datatype float32  
# ephys.segments[0].analogsignals[2] #  2: AnalogSignal with 2 channels of length 13647828; units nA; datatype float32  
# # has 3 'fields':   name: 'Channel bundle (Im-1,Im-2) '
# #                   sampling rate: 40000.0 Hz
# #                   time: 4.9999999999999996e-06 s to 341.195705 s
# ephys.segments[0].analogsignals[2] [:,1]
# # what is the difference between ephys.segments[0].analogsignals[2] [:,1] and 
# Im2=ephys.segments[0].analogsignals[2] [:,0] 



#plot the data
Im = ephys.segments[0].analogsignals[2][:,1] #units of nA
Vm = ephys.segments[0].analogsignals[1][:,1] #units of mW
print(f'Im units: {Im.units}')
print(f'Vm units: {Vm.units}')
print(f'Im sampling rate: {Im.sampling_rate}') #40000.0 Hz for the first 2 channels

fig,axarr = plt.subplots(nrows = 4,sharex = True)
axarr[0].plot(Im.times,np.squeeze(Im))
axarr[0].set_ylabel(f'Membrane Current\n({Im.units})')
axarr[0].set_ylim([-1,1])

axarr[1].plot(Vm.times,np.squeeze(Vm))
axarr[1].set_ylabel(f'Membrane Voltage\n({Vm.units})')
axarr[1].set_ylim([-50,-10])

#This channel shows the command voltage sent to the pockels cell which controls the laser power
pockels = ephys.segments[0].analogsignals[0][:,0]

#this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system
#This measurement has a slow time course and so a calibration run is taken first with longer stimulation duration 
#to enable us to link the 
picker = ephys.segments[0].analogsignals[0][:,1]

axarr[2].plot(pockels.times,np.squeeze(pockels))
axarr[2].set_ylabel('Pockels cell\ncommand voltage (V)')
axarr[3].plot(picker.times,np.squeeze(picker))
axarr[3].set_ylabel('Picker power meter\nmeasurement output (V)')
axarr[3].set_xlabel('Time (s)')
plt.show()


#NOTE that sampling rates for these last two channels is different! 
#Need to use time to compare properly

print(f'Pockels cell sampling rate: {pockels.sampling_rate}')

#load the calibration file
sample_power_calibration = np.loadtxt(calibration_fname)

#plot the calibration
fig,ax = plt.subplots()
ax.plot(sample_power_calibration[0,:],sample_power_calibration[1,:])
ax.set_xlabel('Picker power (mW)')
ax.set_ylabel('Power onto cell (mW)')
plt.show()

#These two constants allow you to convert the voltage measured at the picker 
#into a mW value measured at the picker. The power meter outputs between 0 and picker_max_output Volts
#in direct proportion to the input power as a fraction of picker_max_measurement_mW.
#i.e. if the Picker outputs 1 V, it is measuring 250 mA of current.
picker_max_output_V = 2
picker_max_measurement_mW = 500
beam_spot_diameter = 8 #in micro meters


#this next variable is an array with times and labels which tells us when the calibration and stimulation occurred.
#The label key is in the following dict:
#The keys are loaded as bytes and need to be recovered as characters using the built in chr() function after converting from byte to int
label_key = {'A':'cancel','F':'calibrate','E':'stimulate'}
keyboard = ephys.segments[0].events[1]
labels = [chr(int(x)) for x in keyboard.labels]

print('Trace contains the following events:')
[print(f'Event: {label_key[chr(int(keyboard.labels[x]))]} at time {keyboard[x]:.0f}') for x in range(len(keyboard))]

def get_event_time(event_type,sequence_number,label_key,keyboard,labels):
    # function to get the times of the calibrations
    # event_type (string): based on label keys = 'stimulate' / 'cancel'/ 'calibrate'
    # Sequence number is the sequence for same events i.e. first calibration = 0, first stimulation=0
    event_times=[float(np.where(label_key[chr(int(keyboard.labels[x]))]==event_type,keyboard[x],0)) for x in range(len(keyboard))]
    event_time_indexes=np.nonzero(event_times)
    event_time=event_times[event_time_indexes[0][sequence_number]]
    return event_time
# cal2_time=get_event_time('calibrate',1,label_key,keyboard,labels)
# stim1_time=get_event_time('stimulate',0,label_key,keyboard,labels)
# stim2_time=get_event_time('stimulate',1,label_key,keyboard,labels)
# stim3_time=get_event_time('stimulate',2,label_key,keyboard,labels)


#Task 1:
#turn the Pockels command measurement into optical Power density in the sample (in mW / um^2) using 
#the previous two constants, the calibration curve measured in the pockels time course,
#and the sample_power_calibration (above) which converts between power in the picker and power
#in the sample.

# AS:
############################
#       Threshold
Xdiff=np.diff(np.squeeze(pockels))
# X=np.squeeze(pockels)
# t=pockels.times
# plt.plot(Xdiff[2000000:2500000])
# plt.plot(X[2000000:2500000])

Xdif_threshold=np.where(Xdiff>0.01)
power_on_times=pockels.times[np.where(Xdiff>0.01)]
between_pulse_times=pockels.times[np.where(Xdiff<-0.01)]
power_off_times=pockels.times[np.where((Xdiff>-0.01) & (Xdiff<0.01))]

# calibrations times and samples:
cal_start_time=get_event_time('calibrate',1,label_key,keyboard,labels)
frequency=int(pockels.sampling_rate)
cal_start_sample=int(np.floor(cal_start_time*frequency))
next_event_start=get_event_time('stimulate',0,label_key,keyboard,labels)
next_event_sample=int(np.floor(next_event_start*frequency))
cal_end_time=float(pockels.times[np.where(Xdiff==max(Xdiff[cal_start_sample:next_event_sample]))[0]])
cal_end_sample=int(np.where(Xdiff==max(Xdiff[cal_start_sample:next_event_sample]))[0])

# Pockels command voltage = pockels (V)
X=np.squeeze(pockels[cal_start_sample:cal_end_sample])
t=pockels.times[cal_start_sample:cal_end_sample]
fig=plt.subplots()
plt.plot(t,X)
plt.xlabel('Time (s)')
plt.ylabel('Pockels command voltage (V)')


#Plot the average voltage for each pulse

def pockels_ave_pulse_voltage(pockels,start_sample,end_sample,tol=0.01):
    sample_array=np.squeeze(pockels[start_sample:end_sample])
    times=pockels.times[start_sample:end_sample]
    samples_diff=np.diff(sample_array)
    power_on_times=times[np.where(samples_diff>tol)[0]]
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage
 
power_on_times_c1X,mean_pockels_voltage_c1  =  pockels_ave_pulse_voltage(pockels,cal_start_sample,cal_end_sample)
plt.scatter(power_on_times_c1,mean_pockels_voltage_c1,color='r')
plt.xlabel('Time (s)')
plt.ylabel('Mean pockels command voltage (V)')


# Picker power measurement = picker (V)
Y=np.squeeze(picker[cal_start_sample:cal_end_sample])
t=picker.times[cal_start_sample:cal_end_sample]
fig=plt.subplots()
plt.plot(t,Y)
plt.xlabel('Time (s)')
plt.ylabel('Picker measured voltage (V)')

#Plot the average voltage for each pulse
def picker_ave_pulse_voltage(picker,start_sample,end_sample,pockels_power_on_times):
    sample_array=np.squeeze(picker[start_sample:end_sample])
    power_on_times=pockels_power_on_times
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage

power_on_times_c1Y,mean_picker_voltage_c1 =picker_ave_pulse_voltage(picker,cal_start_sample,cal_end_sample,power_on_times_c1)

plt.plot(power_on_times_c1Y,mean_picker_power,color='r')
plt.xlabel('Time (s)')
plt.ylabel('Mean picker measured voltage (V)')



# Plot input command versus output measurement during calibration time
fig=plt.subplots()
plt.plot(mean_pockels_voltage_c1,mean_picker_voltage_c1)
plt.title('Pockels command voltage (X) versus picker measured voltage (Y)')
plt.xlabel('Mean pockels command voltage (V)')
plt.ylabel('Mean picker measured voltage (V)')


# convert the picker measured output into mW
# As above, power (mW) directly proportional to voltage (V); y=mx 
#These two constants allow you to convert the voltage measured at the picker 
#into a mW value measured at the picker. The power meter outputs between 0 and picker_max_output Volts
#in direct proportion to the input power as a fraction of picker_max_measurement_mW.
#i.e. if the Picker outputs 1 V, it is measuring 250 mA of current.
picker_max_output_V = 2
picker_max_measurement_mW = 500
beam_spot_diameter = 8 #in micro meters
# therefore
m1=picker_max_measurement_mW/picker_max_output_V #Y/X
picker_power_c1=np.squeeze(mean_picker_voltage_c1)*m1 #mW

#Calibration curve power onto cell versus picker power y=mx+c  
m2=np.mean(sample_power_calibration[1,:]/sample_power_calibration[0,:])

# Determine the power onto the cell using calibration curve
Power_onto_cell=m2*picker_power_c1

#Covert to power density: Assume circular spot pi*(d/2)^2 [microns^2]
Power_density=(Power_onto_cell/(np.pi*(beam_spot_diameter/2)**2))

#Plot a curve with pockels cell command voltage (in V) on the x axis, and power density
#in the sample on the y axis.
fig=plt.subplots()
plt.plot(mean_pockels_voltage_c1,Power_density)
plt.title('Power density in sample versus pockels cell command voltage')
plt.xlabel('Pockels cell command voltage (V)')
plt.ylabel('Power density in sample (mW/$\mu$$m^2$)')


#Task 2:
#Segment the measured current values for each stimulation power and repeat.

#AS:
# stimulation time:
stim1_start=250 * 40000
stim1_end= 263 * 40000

# Membrane current (Amps)
t_s1=Im.times[stim1_start:stim1_end]
I_s1=np.squeeze(Im[stim1_start:stim1_end])
plt.plot(t_s1,I_s1)
plt.xlabel('Time (s)')
plt.ylabel(f'Membrane Current\n({Im.units})')

# Membrane voltage (V)
t_s1=Vm.times[stim1_start:stim1_end]
V_s1=np.squeeze(Vm[stim1_start:stim1_end])
plt.plot(t_s1,V_s1)
plt.xlabel('Time (s)')
plt.ylabel(f'Membrane Voltage\n({Vm.units})')

#Plot the average current for each pulse
samples_in_cycle=5000
t_array=[]
max_p_X=[]
for i in range(39): # complete pules
    t_points=217.4944+i*0.4944
    t_array.append(t_points) 
    max_power=np.max(X[i*(samples_in_cycle):samples_in_cycle*(i+1)])
    max_p_X.append(max_power)
plt.scatter(t_array,max_p_X,color='r')
plt.xlabel('Time (s)')
plt.ylabel('Max pockels command voltage (V)')


stim2_start=275 * 10000 
stim2_end=

stim3_start=300 * 10000
stim3_end=

#Plot the Stimulation power - membrane current curve for the first stimulation

#Then plot the 'bleaching' curve: plot the decrease in evoked photocurrent with repeat number.






