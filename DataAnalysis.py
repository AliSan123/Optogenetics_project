os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project')
import numpy as np
import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import scipy.stats
import pandas as pd
import os

os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox')

#file in dropbox
ephys_fname = 'Cell4TCourse.smr'
calibration_fname = 'power_calibration_980nm_8um_spot.dat'
#These two constants allow you to convert the voltage measured at the picker 
#into a mW value measured at the picker. The power meter outputs between 0 and picker_max_output Volts
#in direct proportion to the input power as a fraction of picker_max_measurement_mW.
#i.e. if the Picker outputs 1 V, it is measuring 250 mA of current.
picker_max_output_V = 2
picker_max_measurement_mW = 500
beam_spot_diameter = 8 #in micro meters

def plot_data(X,Y,Xlabel,Ylabel,title,ylim,subplot,show=True,):
    plt.subplot(subplot)
    plt.plot(X,Y)
    plt.ylabel(Ylabel)
    plt.xlabel(Xlabel)
    plt.ylim(ylim)
    plt.title(title)
    if show==True:
        plt.show()

def loadEphysData(FileName,picker_chnl=0,mem_voltage_chnl=1,mem_curr_chnl=0,lazy = False):
     '''
     This function assumes one segment with 3 AnalogSignals,
     picker_chnl,mem_voltage_chnl,mem_curr_chnl assign the channels (set in GUI) or defaults to preset values

     Returns
     -------
     ephys : Block()
         The full unprocessed block item uploaded from the electrophysiological data acquisition board
     picker : Array of float32
         The picker power values at each sampled point
     Vm and Im: Array float32
         The membrane voltage and current respectively at each sampled point
     Vm_units and Im_units: Array of float64
         Units of membrane voltage and current respectively
     Im_Hz and picker_Hz: sampling rates
     '''
     reader = neo.io.Spike2IO(FileName)#load using python-neo
     ephys = reader.read(lazy = lazy)[0]
     # data
     picker = ephys.segments[0].analogsignals[picker_chnl][:,1] #this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.
     Vm = ephys.segments[0].analogsignals[mem_voltage_chnl][:,1] #units of mV
     Im = ephys.segments[0].analogsignals[membrane_current][:,1] #units of nA   
     Vm_units=Vm.units
     Im_units=Im.units
     picker_units=picker.units
     Im_Hz=Im.sampling_rate
     Vm_Hz=Vm.sampling_rate
     picker_Hz=picker.sampling_rate
     
     return ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz

    
# def PlotChannels():
#     ephys,picker,Vm,Im,Vm_units,Im_units, Im_Hz, picker_Hz=loadEphysData()
#     # plot the data
#     plt.figure(1,figsize=(20,15))
#     f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
#         'Picker power meter (measurement output) voltage vs time',None,311,show=False)
#     f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],312,show=False)     
#     f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],313,show=False)
#     plt.savefig(self.TimeDirectory + '//Figure 1- Plot of Ephys Channels.png')
#     plt.show()

def get_event_time(event_type,sequence_number):
    '''
    Parameters
    ----------
    event_type : string * this is assumed to be unchanged
        select event of interest based on label keys = 'stimulate' / 'cancel'/ 'calibrate'
    sequence_number : int
        the sequence for same events i.e. first calibration = 0, first stimulation=0

    Returns
    -------
    event_time : array
        time values corresponding to the event.

    '''
    #this next variable is an array with times and labels which tells us when the calibration and stimulation occurred.   
    #The keys are loaded as bytes and need to be recovered as characters using the built in chr() function after converting from byte to int
    #The label key is in the following dict:
    label_key = {'A':'cancel','F':'calibrate','E':'stimulate'}
    keyboard = ephys.segments[0].events[1]
    labels = [chr(int(x)) for x in keyboard.labels]
    print('Trace contains the following events:')
    [print(f'Event: {label_key[chr(int(keyboard.labels[x]))]} at time {keyboard[x]:.0f}') for x in range(len(keyboard))]
 
    event_times=[float(np.where(label_key[chr(int(keyboard.labels[x]))]==event_type,keyboard[x],0)) for x in range(len(keyboard))]
    event_time_indexes=np.nonzero(event_times)
    event_time=event_times[event_time_indexes[0][sequence_number]]
    return event_time

def plotCalCurve(calibration_fname):
    #load the calibration file
    sample_power_calibration = np.loadtxt(calibration_fname)
    #plot the calibration
    f.plot_data(sample_power_calibration[0,:],sample_power_calibration[1,:],'Picker power (mW)','Power onto cell (mW)',\
            'Calibration curve: Power onto cell vs Picker power',None,show=True)
    plt.show()

def picker_ave_pulse_voltage(picker,start_sample,end_sample,enegy_on_times):
    start_sample=0
    sample_array=np.squeeze(picker[start_sample:end_sample])
    power_on_times=enegy_on_times
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage

        
ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=loadEphysData(ephys_fname)

#  first segment for the pulse duration
start_sample=start_time*sampling_Hz
end_sample=end_time*sampling Hz
picker_power[start_sample:end_sample] #0 to 5ms
# then differentiate to find the maximum power within that section
differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
indexes=np.where(differentiated>0)#these give the indexes of increasing
picker_squeeze=np.squeeze(picker)
indexes_only=picker_squeeze[indexes] #extract only powers of indexes
thres=np.where(indexes_only>0.025) #now apply a threshold
plt.plot(indexes_only[thres])
mean_power_in_section=10 #a single value which is then mapped to the command energy;
#a list is generated
picker_=[mean1,mean2,mean3, etc]
command=[input1, input2, input3, etc]
plot picker_ vs command

picker_power=indexes_only[thres] # this removes the near-zero values







# get_event_time(event_type,sequence_number,label_key,keyboard,labels)

# Energy command into Power density in sample
# Differentiate (before thresholding) - this is to find the sections where TTL=high
picker=np.squeeze(picker)
picker_diff=np.diff(picker)
tolerance=0.01
picker_on=picker[np.where(picker_diff>tolerance)] #this removes periods of little to no changes - extracts periods of energy ON
plt.plot(picker_on)

pockels.times[np.where(picker_diff==max(picker_diff[cal_start_sample:next_event_sample]))[0]

picker_on_indexes=np.where(picker[np.where(picker_diff>tolerance)]>0.1) #this gives the indexes of TTL=HIGH pulses



np.where(picker_on>0.1)
# calibrations times and samples:
cal_start_time=0
frequency=int(picker.sampling_rate)
cal_start_sample=0
cal_end_time=cal_start_time+0.005 #5ms
cal_end_sample=cal_end_time*frequency

# Plot input energy over time
energy_list
time_list
# plot picker power over time
picker_power
time_list

# plot energy versus picker power    
plt.plot(energy_list,picker_power)


    

#  first segment for the pulse duration
start_sample=start_time*sampling_Hz
end_sample=end_time*sampling Hz
picker_power[start_sample:end_sample] #0 to 5ms
# then differentiate to find the maximum power within that section
differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
indexes=np.where(differentiated>0)#these give the indexes of increasing
picker_squeeze=np.squeeze(picker)
indexes_only=picker_squeeze[indexes] #extract only powers of indexes
thres=np.where(indexes_only>0.025) #now apply a threshold
plt.plot(indexes_only[thres])
mean_power_in_section=10 #a single value which is then mapped to the command energy;
#a list is generated
picker_=[mean1,mean2,mean3, etc]
command=[input1, input2, input3, etc]
plot picker_ vs command

picker_power=indexes_only[thres] # this removes the near-zero values



# class DataAnalysis:
#      def __init__(self,ephys_file,calibration_file):
#          self.ephys_file=f.load_ephys(ephys_file)
#          self.calibration_file=calibration_file
        
#          Im = self.ephys_file.segments[0].analogsignals[2][:,1] #units of nA
#          Vm = self.ephys_file.segments[0].analogsignals[1][:,1] #units of mW
#         #this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.
#          picker = ephys.segments[0].analogsignals[0][:,1]
        
#         #plot the figure, save to png in folder, display png?
#          f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],411)
#          f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],412)
#          f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
#             'Picker power meter (measurement output) voltage vs time',None,414)
#          plt.show()
          
#     # this is to find the start of the sequence and remove "breaks"
# #     differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
# # indexes=np.where(differentiated>0)#these give the indexes of increasing
# # picker_squeeze=np.squeeze(picker)
# # indexes_only=picker_squeeze[indexes] #extract only powers of indexes
# # thres=np.where(indexes_only>0.025) #now apply a threshold
# # plt.plot(indexes_only[thres])
        