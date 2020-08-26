import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import numpy as np
from scipy.interpolate import interp1d
import scipy
import pandas

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
    mean_pulse_volts : array
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


def GetCurrent(smrFile,pulse_duration_ms,energy_list,divisor=50,dead_time=2,test=False):
    '''
    Parameters
    ----------
    smrFile : string
        Path to the electrophysiology .smr data file.
    pulse_duration_ms : float
        The time in milliseconds for which the TTL is HIGH.
    energy_list : list
        A list of input RL energy percentages
    divisor : int, optional
        This determines the size of the window around the minimum current. 
        Larger divisor means smaller window for averaging. The default is 50.
    dead_time : int, optional
        A number of seconds of recorded electrophysiology data before the first TTL High signal.
        Used to determine the baseline mean and noise. The default is 2 seconds.
    test : boolean, optional
        For testing, subsets testing data. The default is False.

    Returns
    -------
    min_current_vals : array
        The minimum current values orresponding to the pulses.
    ''' 
    ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=loadEphysData(smrFile)
    if test==True:
        Im=Im[10000000:11000000] #subsetting to simulate real experiment
        #plt.plot(np.squeeze(Im[10072500:10076500])) #This is the first single pulse

    Im_=np.squeeze(Im)
    #Assume a few seconds of dead time for some cleaning:
    dead_samples=int(np.floor(dead_time*Im_Hz))
    Im_dead=Im_[dead_samples:]
    # # find the mean and standard deviation of the voltages when TL is off
    mean=np.mean(Im_dead[0:dead_samples])
    std_dev=np.std(Im_dead[0:dead_samples])
    # first smooth the data 
    duration=int(np.ceil(Im_Hz*(pulse_duration_ms*0.001))) #index of end - make it 1.5 times longer to ensure we capture the maximum
    smoothed_Im=smooth(Im_.flatten(),int(np.floor(duration/4)))
    #use smoothed curve for thresholding
    tol=mean-2*std_dev
    cleaned_Im=Im_[np.where(smoothed_Im.magnitude<tol)] 
    #flip so that the noise at the beginnign is ignored
    cleaned_Im_flipped=np.flip(cleaned_Im)
    #slide the window over dataset and find the local minimum in each window
    window=duration*2
    min_current_vals=[]
    i=0
    for i in range(len(energy_list)):
        sample=cleaned_Im_flipped[(window*i):(window*(i+1))]
        min_sample_index=np.asarray(np.where(sample==min(sample))).ravel()[0]
        #the buffer is the points around the minimum value which we'll average to reduce noise
        buffer=int(np.floor(duration/divisor))
        min_sample_ave=np.mean(sample[min_sample_index-buffer:min_sample_index +buffer])
        min_current_vals.append(min_sample_ave)
        i+=1
        #plt.plot(mins)
    min_current_vals=np.flip(min_current_vals)
    return min_current_vals

def sigmoid(x, L ,a, b, c):
    y = L / (1 + np.exp(-a*(x-b)))+c
    return y    

def Michaelis_Menten_model(P,Imax,Kd):
    Ipeak=Imax*P/(P+Kd)
    return Ipeak

def getKd(power_data,current_data):
    popt,pcov=scipy.optimize.curve_fit(Michaelis_Menten_model,power_data,current_data)
    return popt[1]

def getFromCalibration(cal_energy_list,cal_power_density):
    p0=[max(cal_power_density), np.median(cal_energy_list),1,min(cal_power_density)] # this is an mandatory initial guess
    popt,pcov=scipy.optimize.curve_fit(sigmoid,cal_energy_list,cal_power_density,p0,method='dogbox')
    x=new_energy_list
    L=popt[0]
    a=popt[1]
    b=popt[2]
    c=popt[3]
    new_Power_Density=sigmoid(x,L,a,b,c)
    new_Power=new_Power_Density*(np.pi*(beam_diameter/2)**2)
    return new_Power_Density, new_Power

def getMRRfromEnergy(energy_power_calibration,Kd):
    cal_energy_list=energy_power_calibration['cal_energy_list']
    cal_power_density=energy_power_calibration['Power_density']
    power_density,power=f.getFromCalibration(cal_energy_list,cal_power_density) #power in mW        
    MRR_in_kHz=(power**2)/Kd
    return power density, power, MRR_in_kHz

def getPowerfromMRR(MRR_in_kHz,)):
    power=sqrt(MRR_in_kHz*Kd)

if __name__=='__main__':  
    file=r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox\Cell4TCourse.smr'
    pulse_duration_ms=200# 0.1 seconds
    energy_list1=np.linspace(0,1.4,39)
    mean_picker_volts=GetMeanVolts(file,pulse_duration_ms,energy_list1,dead_time=2,test=True)
    #plt.plot(energy_list,mean_picker_volts)
    picker_max_output_V = 2
    picker_max_measurement_mW = 500
    beam_spot_diameter = 8 #in micro meters
    calibration_fname=r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox\power_calibration_980nm_8um_spot.dat'
    Power_density=convert_V_W(mean_picker_volts,picker_max_measurement_mW,picker_max_output_V,calibration_fname,beam_spot_diameter)
    #plt.plot(energy_list1,Power_density)
    #interpolate
    # f=interp1d(energy_list1,Power_density)
    new_energy_list=np.linspace(0,0.4,30)
    # new_Power_Density=f(new_energy_list)
    # #Or use curve fit function
    p0=[max(Power_density), np.median(energy_list1),1,min(Power_density)] # this is an mandatory initial guess
    popt,pcov=scipy.optimize.curve_fit(sigmoid,energy_list1,Power_density,p0,method='dogbox')
    x=new_energy_list
    L=popt[0]
    a=popt[1]
    b=popt[2]
    c=popt[3]
    Power_Density_new=sigmoid(x,L,a,b,c)
    plt.plot(new_energy_list,Power_Density_new,'-')
    
    #plt.plot(energy_list,Power_density,'o',x,new_Power_Density,'-')
    
    # pulse_duration_ms=5
    # min_current_vals=GetCurrent(file,pulse_duration_ms,energy_list,divisor=50,dead_time=2,test=True)
    # #plt.plot(min_current_vals)
    # beam_diameter=8
    # current_density=min_current_vals/(np.pi*(beam_diameter/2)**2)
    # Kd=getKd(new_Power_Density,current_density)
    # xnew=cell_energy_list
    # new_power_density=f(xnew) # these give the power densities of the new energy list
    # current_density=min_current_vals/(np.pi*(beam_diameter/2)**2)
    # plt.plot(new_power_density,current_density) #this is what you use to extract kd

    
    # Imax=max(current_density)
    # I_half_max=Imax/2
    # f2=interp1d(new_power_density,current_density,axis=0)#interpolate x-axis
    # ynew=I_half_max
    # xnew=f2(ynew))
