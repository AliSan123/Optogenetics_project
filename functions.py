import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import numpy as np

def plot_data(X,Y,Xlabel,Ylabel,title,ylim,subplot,show=True):
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


# Code sourced from Divakar (2016)
def smooth(signal,window):
    '''
    Parameters
    ----------
    signal : numpy 1D array  = The signal data to be smoothed
    window : int  =    The window size for smoothing.
    Returns
    -------
    smoothed array=   The signal data now smoothed.
    '''
    #window must be odd as in the original matlab implementation
    if (window % 2) ==0: #checks if number is even
        window=window+1 # make it odd 
    else:
        window=window
    out0 = np.convolve(signal,np.ones(window,dtype=int),'valid')/window    
    r = np.arange(1,window-1,2)
    start = np.cumsum(signal[:window-1])[::2]/r
    stop = (np.cumsum(signal[:-window:-1])[::2]/r)[::-1]
    return np.concatenate((  start , out0, stop  ))


def GetMeanVolts(smrFile,pulse_duration_ms,energy_list,dead_time=2,test=False):
    '''
    Parameters
    ----------
    smrFile : string 
        Path to the electrophysiology .smr data file
    pulse_duration_ms : float
        The time in milliseconds for which the TTL is HIGH 
    energy_list : list
        A list of input RL energy percentages
    dead_time : float, optional
        A portion of the time between switching on the electrophysiolgy data 
        recording and sending the first TTL=High pulse. This is used to establish a baseline
        for when the TTL is LOW. The default is 2 seconds.
    test : boolean, optional
        Runs certain lines for testing only. The default is False.

    Returns
    -------
    mean_pulse_volts : list
        The mean picker volts.

    '''
    ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=loadEphysData(smrFile)
    if test==True:
        picker=picker[:2530000] #subsetting to simulate real experiment
    picker_=np.squeeze(picker)
    #Assume a few seconds of dead time for some cleaning:
    dead_samples=int(np.floor(dead_time*picker_Hz))
    picker_dead=picker_[dead_samples:]
    # find the mean and standard deviation of the voltages when TL is off
    mean=np.mean(picker_dead[0:dead_samples])
    std_dev=np.std(picker_dead[0:dead_samples])
    # first smooth the data 
    duration=int(np.ceil(picker_Hz*pulse_duration_ms*0.001*1.5)) #index of end - make it 1.5 times longer to ensure we capture the maximum
    smoothed_picker=smooth(picker_.flatten(),int(np.floor(duration/4)))
    #use smoothed curve for thresholding
    tol=mean+2*std_dev
    cleaned_picker=picker_[np.where(smoothed_picker.magnitude>tol)]    
    #flip so that it goes from maximum to minimum volts
    # This makes it easier to calculate the mean pulse energies once picker has ramped up
    cleaned_picker_flipped=np.flip(cleaned_picker)        
    # get the number of pulses deployed using what was sent in the code
    n_pulses=len(energy_list)
    # Find the start of each pulse in the calibration using maximum energy less tolerance
    # Average energy over half the pulse duration (once it has ramped up)
    start=0
    sample=cleaned_picker_flipped
    mean_pulse_volts=[]
    for i in range(n_pulses):
        sample=sample[start:]
        max_sample=max(sample.magnitude)
        tolN=max_sample-2*std_dev.magnitude
        pulse_start=np.where(sample>tolN)[0][0] #this is the start within the sample
        pulse_duration_ms=200
        pulse_end=int(np.floor(pulse_start+pulse_duration_ms*0.001*picker_Hz.magnitude))
        #plt.plot(sample[pulse_start:pulse_end])
        # find the average energy over half the pulse duration
        half_pulse_end=int(np.floor(pulse_start+pulse_duration_ms/2*0.001*picker_Hz.magnitude))
        half_pulse=sample[pulse_start:half_pulse_end]
        mean_pulse_volt=np.mean(half_pulse)
        mean_pulse_volts.append(mean_pulse_volt)
        start=pulse_end
    
    #flip again so that back to original order
    mean_pulse_volts=np.flip(mean_pulse_volts
                             )
    return mean_pulse_volts

    
def convert_V_W(mean_pulse_volts,picker_max_measurement_mW,picker_max_output_V,calibration_fname,beam_diameter):
    #power (mW) directly proportional to voltage (V); y=mx
    m=picker_max_measurement_mW/picker_max_output_V #Y/X
    picker_power=mean_pulse_volts*m
    #Calibration curve power onto cell versus picker power y=mx+c
    calibration_file = np.loadtxt(calibration_fname)
    power_onto_cell_mW=calibration_file[1,:]
    cal_picker_power_mW=calibration_file[0,:]
    m2=np.mean(power_onto_cell_mW/cal_picker_power_mW)
    #Find Power onto cell using calibration curve
    Power_onto_cell=m2*picker_power
    #Covert to power density: Assume circular spot pi*(d/2)^2 [microns^2]
    Power_density=(Power_onto_cell/(np.pi*(beam_diameter/2)**2))
    #   return energy_vs_power
    return  Power_density


# plot of stimulation power versus membrane current




if __name__=='__main__':  
    file=r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox\Cell4TCourse.smr'
    pulse_duration_ms=100# 0.1 seconds
    energy_list=np.linspace(0,1.5,39)
    mean_picker_volts=GetMeanVolts(file,pulse_duration_ms,energy_list,dead_time=2,test=True)
    plt.plot(energy_list,mean_picker_volts)
    picker_max_output_V = 2
    picker_max_measurement_mW = 500
    beam_spot_diameter = 8 #in micro meters
    calibration_fname=r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox\power_calibration_980nm_8um_spot.dat'
    Power_density=convert_V_W(mean_picker_volts,picker_max_measurement_mW,picker_max_output_V,calibration_fname,beam_spot_diameter)
    plt.plot(energy_list,Power_density)