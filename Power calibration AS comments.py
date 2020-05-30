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
ephys.segments[0] # Only contains 1 segment with 3 chennels:
                  #  0: AnalogSignal with 2 channels of length 3411957; units V; datatype float32 
                  #  1: AnalogSignal with 2 channels of length 13647828; units mV; datatype float32
                  #  2: AnalogSignal with 2 channels of length 13647828; units nA; datatype float32  
ephys.segments[0].analogsignals[2] #  2: AnalogSignal with 2 channels of length 13647828; units nA; datatype float32  
# has 3 'fields':   name: 'Channel bundle (Im-1,Im-2) '
#                   sampling rate: 40000.0 Hz
#                   time: 4.9999999999999996e-06 s to 341.195705 s
ephys.segments[0].analogsignals[2] [:,1]
# what is the difference between ephys.segments[0].analogsignals[2] [:,1] and 
Im2=ephys.segments[0].analogsignals[2] [:,0] 



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



#Task 1:
#turn the Pockels command measurement into optical Power density in the sample (in mW / um^2) using 
#the previous two constants, the calibration curve measured in the pockels time course,
#and the sample_power_calibration (above) which converts between power in the picker and power
#in the sample.

# AS:
# calibrations time:
cal_start=217 * 10000 
cal_end= 237 * 10000

# Pockels command voltage = pockels (V)
X=np.squeeze(pockels[cal_start:cal_end])
t=pockels.times[cal_start:cal_end]
fig=plt.subplots()
plt.plot(t,X)
plt.xlabel('Time (s)')
plt.ylabel('Pockels command voltage (V)')

#Plot the average voltage for each pulse
samples_in_cycle=5000
t_array=[]
max_p_X=[]
for i in range(39): # complete pulses
    t_points=217.4944+i*0.4944
    t_array.append(t_points) 
    max_power=np.max(X[i*(samples_in_cycle):samples_in_cycle*(i+1)])
    max_p_X.append(max_power)
plt.scatter(t_array,max_p_X,color='r')
plt.xlabel('Time (s)')
plt.ylabel('Max pockels command voltage (V)')


# Picker power measurement = picker (V)
Y=np.squeeze(picker[cal_start:cal_end])
t=picker.times[cal_start:cal_end]
fig=plt.subplots()
plt.plot(t,Y)
plt.xlabel('Time (s)')
plt.ylabel('Picker measured voltage (V)')

#Plot the average voltage for each pulse
samples_in_cycle=5000
t_array=[]
max_p_Y=[]
for i in range(39): #  pules
    t_points=217.4944+i*0.4944
    t_array.append(t_points) 
    max_power=np.max(Y[i*(samples_in_cycle+1):samples_in_cycle*(i+1)])
    max_p_Y.append(max_power)

plt.plot(t_array,max_p_Y,color='r')
plt.xlabel('Time (s)')
plt.ylabel('Max picker measured voltage (V)')

# Plot input command versus output measurement during calibration time
fig=plt.subplots()
plt.plot(max_p_X,max_p_Y)
plt.title('Pockels command voltage (Y) versus picker measured voltage (X)')
plt.xlabel('Pockels command voltage (V)')
plt.ylabel('Picker measured voltage (V)')


# convert the picker measured output into mW
# As above, power (mW) directly proportional to voltage (V); y=mx - y=250x
picker_power=np.squeeze(max_p_Y)*250 #mW

#Calibration curve power onto cell versus picker power y=mx+c  Y=5.7655X
m=np.mean(sample_power_calibration[1,:]/sample_power_calibration[0,:]) #Y/X

# Determine the power onto the cell using calibration curve
Power_onto_cell=m*picker_power

#Covert to power density: Assume circular spot pi*(d/2)^2 [microns^2]
Power_density=(Power_onto_cell/(np.pi*(beam_spot_diameter/2)**2))

#Plot a curve with pockels cell command voltage (in V) on the x axis, and power density
#in the sample on the y axis.
fig=plt.subplots()
plt.plot(max_p_X,Power_density)
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