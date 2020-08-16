import numpy as np
import matplotlib.pyplot as plt
import neo #https://neo.readthedocs.io/en/stable/
import scipy.stats
import pandas as pd
import os

os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project')

class DataAnalysis:
    def __init__(self,ephys_file,calibration_file):
        