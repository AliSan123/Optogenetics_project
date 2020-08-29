# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 21:29:53 2020

@author: user
"""

os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Dropbox')


import numpy as np
import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import scipy.stats
import pandas as pd
import functions as f


#file in dropbox
ephys_fname = 'Cell4TCourse.smr'
calibration_fname = 'power_calibration_980nm_8um_spot.dat'

#load using python-neo
ephys = f.load_ephys(ephys_fname)
pd.DataFrame(np.squeeze(ephys.segments[0].analogsignals[0]))
np.squeeze(ephys)
# 1: Channel bundle Pockels, PickerPow with 2 channels V
ephys.segments[0].analogsignals[0]

# 2: Channel bundle with 2 channels Vm-1, Vm-2
ephys.segments[0].analogsignals[1]

# 3: Channel bundle with Im-1,Im-2
ephys.segments[0].analogsignals[2]

picker = ephys.segments[0].analogsignals[0][:,1]