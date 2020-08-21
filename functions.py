import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import numpy as np

def plot_data(X,Y,Xlabel,Ylabel,title,ylim,subplot,show=True,):
    plt.subplot(subplot)
    plt.plot(X,Y)
    plt.ylabel(Ylabel)
    plt.xlabel(Xlabel)
    plt.ylim(ylim)
    plt.title(title)
    if show==True:
        plt.show()

def loadEphysData(FileName,picker_chnl=0,mem_voltage_chnl=1,mem_curr_chnl=2,lazy = False):
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
     Im = ephys.segments[0].analogsignals[mem_curr_chnl][:,1] #units of nA   
     Vm_units=Vm.units
     Im_units=Im.units
     picker_units=picker.units
     Im_Hz=Im.sampling_rate
     Vm_Hz=Vm.sampling_rate
     picker_Hz=picker.sampling_rate
     
     return ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz

#These two constants allow you to convert the voltage measured at the picker 
#into a mW value measured at the picker. The power meter outputs between 0 and picker_max_output Volts
#in direct proportion to the input power as a fraction of picker_max_measurement_mW.
#i.e. if the Picker outputs 1 V, it is measuring 250 mA of current.
# picker_max_output_V = 2
# picker_max_measurement_mW = 500
# beam_spot_diameter = 8 #in micro meters 


 #Step 1 - use event labels to get when calibration events occurred
def get_event_time(ephys,event_type,sequence_number):
    '''
    Parameters
    ----------
    ephys : Block ()
        fetched from function loadEphysData()
    event_type : string * this is assuming labels are consistent
        select event of interest based on label keys = 'stimulate' / 'cancel'/ 'calibrate'
    sequence_number : int
        the sequence for same events i.e. first calibration = 0, first stimulation=0

    Returns
    -------
    event_time : array
        time values corresponding to the start of an event.

    '''
    #this next variable is an array with times and labels which tells us when the calibration and stimulation occurred.   
    #The keys are loaded as bytes and need to be recovered as characters using the built in chr() function after converting from byte to int
    #The label key is in the following dict:
    label_key = {'A':'cancel','F':'calibrate','E':'stimulate'}
    keyboard = ephys.segments[0].events[1]
    #labels = [chr(int(x)) for x in keyboard.labels]
    print('Trace contains the following events:')
    [print(f'Event: {label_key[chr(int(keyboard.labels[x]))]} at time {keyboard[x]:.0f}') for x in range(len(keyboard))]
 
    event_times=[float(np.where(label_key[chr(int(keyboard.labels[x]))]==event_type,keyboard[x],0)) for x in range(len(keyboard))]
    event_time_indexes=np.nonzero(event_times)
    event_time=event_times[event_time_indexes[0][sequence_number]]
    return event_time

#start_time= get_event_time(ephys,event_type,sequence_number)
    #Step 2 -- segment the event of interest 
    #Step 3 - get the mean power over the segment
def picker_calibration_segment(start_time,time_list,picker_Hz,picker,steps,n_times,tol=0.01):#variable_list,picker,picker_max_output_V,picker_max_measurement_mW,beam_spot_diameter):
    ##  first define the event duration
    Xdiff=np.diff(np.squeeze(picker))
    
    start_sample=int(np.floor(start_time*picker_Hz))
    end_time=start_time+max(time_list)
    approx_end_sample=int(np.ceil(end_time*picker_Hz))
    max_dif=max(np.where(Xdiff==max(Xdiff[start_sample:approx_end_sample])))
    print(max_dif)
    exact_end_time=max(picker.times[max_dif])
    end_sample=int(np.ceil(exact_end_time*picker_Hz))
    segment=np.squeeze(picker[start_sample:end_sample]) # powers corresponding to calibration time
    # plt.plot(segment)
    
    segment_times=picker.times[start_sample:end_sample]
    segment_diff=np.diff(segment) # This highlights extremes changes (i.e. On and Off)
    TTL_high_times=segment_times[np.where(segment_diff>tol)[0]]
    print(TTL_high_times)
    #number_pulses=steps*n_times
    number_pulses=len(TTL_high_times)
    print(number_pulses)
    samples_per_pulse=int(np.ceil((end_sample-start_sample)/(number_pulses+1)))
    mean_voltage=[np.max(segment[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(number_pulses)]
    plt.plot(TTL_high_times,mean_voltage)
    


def pockels_ave_pulse_voltage(pockels,start_sample,end_sample,tol=1):
    sample_array=np.squeeze(pockels[start_sample:end_sample])
    times=pockels.times[start_sample:end_sample]
    samples_diff=np.diff(sample_array)
    power_on_times=times[np.where(samples_diff>tol)[0]]
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage 
# 
# def picker_ave_pulse_voltage(picker,start_sample,end_sample,pockels_power_on_times):
#     sample_array=np.squeeze(picker[start_sample:end_sample])
#     power_on_times=pockels_power_on_times
#     num_pulses=len(power_on_times)
#     samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
#     mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
#     return power_on_times, mean_voltage





    
    #   # then differentiate to find the maximum power within that section
  #   differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
  #   indexes=np.where(differentiated>0)#these give the indexes of increasing
  #   picker_squeeze=np.squeeze(picker)
  #   indexes_only=picker_squeeze[indexes] #extract only powers of indexes
  #   thres=np.where(indexes_only>0.025) #now apply a threshold
  #   plt.plot(indexes_only[thres])
  #   mean_power_in_section=10 #a single value which is then mapped to the command energy;
  #   #a list is generated
  #   picker_=[mean1,mean2,mean3, etc]
  #   command=[input1, input2, input3, etc]
  #   plot picker_ vs command
  
  # variable_list
    
    
  #   return energy_vs_power
if __name__=='__main__':  
    file=r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox\Cell4TCourse.smr'
    ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=loadEphysData(file)
    start_time=get_event_time(ephys,event_type='calibrate',sequence_number=1)
    time_list=[0,5,10,15,25]
    picker_calibration_segment(start_time,time_list,picker_Hz,picker,0,0)
# energy_list(5 5 5 10 10 10)