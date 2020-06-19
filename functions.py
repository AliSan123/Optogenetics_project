# File for Functions
import neo #https://neo.readthedocs.io/en/stable/
import matplotlib.pyplot as plt
import numpy as np

def load_ephys(path,lazy = False):
    reader = neo.io.Spike2IO(path)
    bl = reader.read(lazy = lazy)[0]
    return bl

def plot_data(X,Y,Xlabel,Ylabel,title,subplot=111):
    plt.subplot(subplot)
    plt.plot(X,Y)
    plt.ylabel(Ylabel)
    plt.xlabel(Xlabel)
    plt.title(title)

def get_event_time(event_type,sequence_number,label_key,keyboard,labels):
    # function to get the times of the calibrations
    # note sequence number refers to the sequence for same events i.e. first calibration = 0, first stimulation=0
    event_times=[float(np.where(label_key[chr(int(keyboard.labels[x]))]==event_type,keyboard[x],0)) for x in range(len(keyboard))]
    event_time_indexes=np.nonzero(event_times)
    event_time=event_times[event_time_indexes[0][sequence_number]]
    return event_time

def ave_pulse_voltage(array,start_sample,end_sample,tol=0.01,powerOn_times=None):
    sample_array=np.squeeze(array[start_sample:end_sample])
    times=array.times[start_sample:end_sample]
    samples_diff=np.diff(np.squeeze(array[start_sample:end_sample]))
    if powerOn_times is None:
        power_on_times=times[np.where(samples_diff>tol)[0]]
    else:
        power_on_times=powerOn_times
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_power=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_power
 