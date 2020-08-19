# File for Functions
import neo #https://neo.readthedocs.io/en/stable/
import matplotlib.pyplot as plt
import numpy as np

def load_ephys(path,lazy = False):
    reader = neo.io.Spike2IO(path)
    bl = reader.read(lazy = lazy)[0]
    return bl

def plot_data(X,Y,Xlabel,Ylabel,title,ylim,subplot=111,show=True):
    plt.subplot(subplot)
    plt.plot(X,Y)
    plt.ylabel(Ylabel)
    plt.xlabel(Xlabel)
    plt.ylim(ylim)
    plt.title(title)
    if show==True:
        plt.show()

def get_event_time(event_type,sequence_number,label_key,keyboard,labels):
    # function to get the times of the calibrations
    # event_type (string): based on label keys = 'stimulate' / 'cancel'/ 'calibrate'
    # Sequence number is the sequence for same events i.e. first calibration = 0, first stimulation=0
    event_times=[float(np.where(label_key[chr(int(keyboard.labels[x]))]==event_type,keyboard[x],0)) for x in range(len(keyboard))]
    event_time_indexes=np.nonzero(event_times)
    event_time=event_times[event_time_indexes[0][sequence_number]]
    return event_time


def pockels_ave_pulse_voltage(pockels,start_sample,end_sample,tol=0.01):
    sample_array=np.squeeze(pockels[start_sample:end_sample])
    times=pockels.times[start_sample:end_sample]
    samples_diff=np.diff(sample_array)
    power_on_times=times[np.where(samples_diff>tol)[0]]
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage 
 
def picker_ave_pulse_voltage(picker,start_sample,end_sample,pockels_power_on_times):
    sample_array=np.squeeze(picker[start_sample:end_sample])
    power_on_times=pockels_power_on_times
    num_pulses=len(power_on_times)
    samples_per_pulse=int(np.floor((end_sample-start_sample)/(num_pulses+1)))
    mean_voltage=[np.mean(sample_array[(i)*(samples_per_pulse):samples_per_pulse*(i+1)]) for i in range(num_pulses)]
    return power_on_times, mean_voltage
    