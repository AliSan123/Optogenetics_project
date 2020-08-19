import numpy as np
import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import scipy.stats
import pandas as pd
import os

import functions as f

os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project')


#file in dropbox
ephys_fname = 'Cell4TCourse.smr'
calibration_fname = 'power_calibration_980nm_8um_spot.dat'

#load using python-neo
ephys = f.load_ephys(ephys_fname)

# data
Im = ephys.segments[0].analogsignals[2][:,1] #units of nA
Vm = ephys.segments[0].analogsignals[1][:,1] #units of mW
#This channel shows the command voltage sent to the pockels cell which controls the laser power
pockels = ephys.segments[0].analogsignals[0][:,0] 
#this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.
picker = ephys.segments[0].analogsignals[0][:,1] 

class DataAnalysis:
     def __init__(self,ephys_file,calibration_file):
         self.ephys_file=f.load_ephys(ephys_file)
         self.calibration_file=calibration_file
        
         Im = self.ephys_file.segments[0].analogsignals[2][:,1] #units of nA
         Vm = self.ephys_file.segments[0].analogsignals[1][:,1] #units of mW
        #this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.
         picker = ephys.segments[0].analogsignals[0][:,1]
        
        #plot the figure, save to png in folder, display png?
         f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],411)
         f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],412)
         f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
            'Picker power meter (measurement output) voltage vs time',None,414)
         plt.show()
          
    # this is to find the start of the sequence and remove "breaks"
#     differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
# indexes=np.where(differentiated>0)#these give the indexes of increasing
# picker_squeeze=np.squeeze(picker)
# indexes_only=picker_squeeze[indexes] #extract only powers of indexes
# thres=np.where(indexes_only>0.025) #now apply a threshold
# plt.plot(indexes_only[thres])
        