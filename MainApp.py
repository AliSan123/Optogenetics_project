# arduino.close_port()
# coherent.close_port()

import os
os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project')

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog
from icons_rc import *
import sys
import webbrowser
import datetime
import pandas as pd
import numpy as np
import shutil
import Coherent
import Arduino
import functions as f
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

SafetyWindow_ui,_=uic.loadUiType('SafetyWindow.ui')
UploadPowCalResults_ui,_=uic.loadUiType('UploadPowCalResults.ui')

class Ui(QtWidgets.QMainWindow):
    def __init__(self,arduino,coherent):
        super(Ui,self).__init__() #call the inherited classes __init__method
        uic.loadUi('MainApp.ui',self) # Load the .ui file
                
        #serial ports
        self.arduino=arduino
        self.coherent=coherent
        
        #       HOME SCREEN      
        self.TCs_button1.clicked.connect(self.OpenTermsOfUse)
        self.read_checkbox.clicked.connect(self.SetupColourtoGreen)
        self.SetupButton.clicked.connect(self.GoToSetupTab)

#       SETUP TAB
        self.BrowseButton1.clicked.connect(self.SelectProjectFolder) 
        self.set1.clicked.connect(self.SetProjectDirectory)
        self.CreateExpFolder.clicked.connect(self.clickedCreateExpFolder)
        self.set2.clicked.connect(self.SetExpDirectory)
        self.CreateDailyFolder.clicked.connect(self.clickedCreateDailyFolder)
        self.set3.clicked.connect(self.SetDailyDirectory)
        self.CreateTimeFolder.clicked.connect(self.clickedCreateTimeFolder)
        self.set4.clicked.connect(self.SetTimeDirectory)
        self.BrowseButton2.clicked.connect(self.UploadCalibrationFile)
        self.NextButton.clicked.connect(self.GoToPowerCalibration)

#       POWER CALIBRATION TAB    
        
        self.setParams.clicked.connect(self.getParamVals) 
        self.setParams.clicked.connect(self.RunButtonToGreen)
        self.RunButton.clicked.connect(lambda: self.OpenSafetyWindow('Power'))

#       MRR CALIBRATION TAB 
        self.setMRRParams.clicked.connect(self.getMRRParamVals) 
        self.setMRRParams.clicked.connect(self.RunButtonToGreen2)
        self.RunButton_2.clicked.connect(lambda: self.OpenSafetyWindow('MRR'))
        
#       HOME SCREEN  
    def OpenTermsOfUse(self):
        TOU=TermsOfUse()
        TOU.exec_()
    
    def SetupColourtoGreen(self):
        self.SetupButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.SetupButton.setIcon(icon)
    
    def GoToSetupTab(self):
        self.tabWidget.setCurrentIndex(1)

#       SETUP TAB
    def SelectProjectFolder(self):
        FolderDirectory=QFileDialog.getExistingDirectory(self,'Open Directory','Project Folder',QFileDialog.ShowDirsOnly)
        self.lineEditDirectory.setText(FolderDirectory)
        # create subfolders within this: experiments; daily dates
    
    def SetProjectDirectory(self):
        FolderDirectory=self.lineEditDirectory.text() #in case the user edits the directory
        os.chdir(FolderDirectory)
        self.set1.setStyleSheet("font: 8pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        return FolderDirectory
    
    def createFolder(self,directory):
        try: 
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error creating folder' + directory)  
    
    def clickedCreateExpFolder(self):
        self.createFolder('./Experiments/')
        ExperimentsDirectory=os.getcwd()+'\Experiments'
        self.lineEditDirectory_2.setText(ExperimentsDirectory)

    def SetExpDirectory(self):
        ExperimentsDirectory=self.lineEditDirectory_2.text()
        os.chdir(ExperimentsDirectory)
        self.set2.setStyleSheet("font: 8pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        return ExperimentsDirectory
    
    def clickedCreateDailyFolder(self):
        self.createFolder(datetime.datetime.now().strftime('%Y-%m-%d'))
        DailyDirectory=os.getcwd() + datetime.datetime.now().strftime('\%Y-%m-%d')
        self.lineEditDirectory_3.setText(DailyDirectory)
        
    def SetDailyDirectory(self):
        DailyDirectory=self.lineEditDirectory_3.text()
        os.chdir(DailyDirectory)
        self.set3.setStyleSheet("font: 8pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        
    def getDailyDirectory(self):
        DailyDirectory=self.lineEditDirectory_3.text()
        return DailyDirectory
    
    def clickedCreateTimeFolder(self):
        self.createFolder(datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%S'))
        TimeDirectory=os.getcwd() + datetime.datetime.now().strftime('\%Y-%m-%d_%Hh%Mm%S')
        self.lineEditDirectory_4.setText(TimeDirectory)
    
    def SetTimeDirectory(self):
        TimeDirectory=self.lineEditDirectory_4.text()
        os.chdir(TimeDirectory)
        self.set4.setStyleSheet("font: 8pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")       
    
    def getTimeDirectory(self):
        TimeDirectory=self.lineEditDirectory_4.text()
        return TimeDirectory 
    
    def UploadCalibrationFile(self):
        calibration_fname,_filter=QFileDialog.getOpenFileName(self, 'Upload File')
        newPath=shutil.copy(calibration_fname,self.getDailyDirectory() + '\\' + 'power_calibration_980nm_8um_spot -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.dat')
        self.lineEditFile.setText(newPath)      
        self.NextButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NextButton.setIcon(icon)     

    def GoToPowerCalibration(self):
        self.tabWidget.setCurrentIndex(2)

#       POWER CALIBRATION
    def OpenSafetyWindow(self,Type): 
        steps=0 #giving it a value because not applicable for 'MRR'
        if Type=='Power':
            MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval,steps=self.getParamVals()
        elif Type=='MRR':
            MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval=self.getMRRParamVals()
            
        TimeDirectory=self.getTimeDirectory()
        DailyDirectory=self.getDailyDirectory()
        SW=SafetyWindow(self.arduino,self.coherent,Type,DailyDirectory,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps)
        SW.exec_()
        
    def getParamVals(self):
        #Repetition rate parameters
        combo_txt=self.comboBox.currentText()
        combo_lst=combo_txt.split(",")
        MRR_in_kHz=combo_lst[0]
        PW_in_fs=combo_lst[1]
        RRDivisor=combo_lst[2]
        PulsesPerMBurst=combo_lst[3]
        # energy params
        min_energy_as_frac=self.energy_spinbox.value()/100
        print('min energy as frac= %i'%min_energy_as_frac)
        max_energy_as_frac=self.energy_spinbox_2.value()/100
        print('max energy as frac= %i'%max_energy_as_frac)
        steps=self.energy_spinbox_3.value()
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
        pulse_duration_ms=self.CalTimeSpinBox.value()        
        interpulseinterval=self.IPISpinBBox.value()
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,pulse_duration_ms,n_times,interpulseinterval,steps
              
    def RunButtonToGreen(self):
        self.RunButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RunButton.setIcon(icon)
        
# MRR Calibration
    def getMRRParamVals(self):
        #Repetition rate parameters   
        combo_txt=self.MRRcomboBox.currentText()
        combo_lst=combo_txt.split(",") 
        MRR_in_kHz=combo_lst
        print('MRR list:' + str(MRR_in_kHz))
        PW_in_fs=self.PWdoubleSpinBox.value()
        RRDivisor=1
        PulsesPerMBurst=1
        # energy params
        energy_as_frac=self.energy_spinbox_5.value()/100
        n_times=self.MRR_spinbox.value()
        pulse_duration_ms=self.CalTimeSpinBox_2.value()        
        interpulseinterval=self.IPISpinBBox_2.value()
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval
    
    def RunButtonToGreen2(self):
        self.RunButton_2.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RunButton_2.setIcon(icon)
                    


        
class SafetyWindow(QDialog,SafetyWindow_ui):
    def __init__(self,arduino,coherent,Type,DailyDirectory,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval,steps=0):
        QDialog.__init__(self)
        SafetyWindow_ui.__init__(self)
        self.setupUi(self)
        
        self.Type=Type
        self.arduino=arduino
        self.coherent=coherent
        self.TimeDirectory=TimeDirectory
        self.DailyDirectory=DailyDirectory
        
        self.MRR_in_kHz=MRR_in_kHz
        self.PW_in_fs=PW_in_fs
        self.RRDivisor=RRDivisor
        self.PulsesPerMBurst=PulsesPerMBurst
        self.energy_as_frac=energy_as_frac
        self.pulse_duration_ms=pulse_duration_ms
        self.n_times=n_times
        self.steps=steps   
        self.interpulseinterval=interpulseinterval          
        
        self.checkBoxKeyswitch.stateChanged.connect(self.ChangeColour)
        self.LaserManualButton2.clicked.connect(self.OpenLaserManual) 
        self.SWRunButton.clicked.connect(self.StartLaserCalibration)           
        
    def ChangeColour(self):          
        if self.checkBoxIsSafe.isChecked() and self.checkBoxKeyswitch.isChecked():
            self.SWRunButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.SWRunButton.setIcon(icon)
    
    def OpenLaserManual(self):
        path=r'https://edge.coherent.com/assets/pdf/COHR_Monaco1035_DS_0120_1.pdf'
        webbrowser.open(path)
                  
    def StartLaserCalibration(self):
        self.coherent.startup()
        if self.Type=='Power':
            self.coherent.set_MRR(self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst)
            for i in range(self.steps):
                print(self.energy_as_frac*(i+1))
                self.coherent.set_energy(self.energy_as_frac*(i+1))
                self.coherent.start_lasing()               
                self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, self.interpulseinterval)
            self.coherent.stop_lasing()
            print('Completed lasing')
            self.close() # close window
            #Open new window for results
            NewWindow=UploadResults(self.TimeDirectory,self.Type)
        elif self.Type=='MRR':
            self.coherent.startup()
            self.coherent.set_energy(self.energy_as_frac)
            for i in range(len(self.MRR_in_kHz)):
                print(len(self.MRR_in_kHz))
                print(self.MRR_in_kHz[i])
                self.coherent.set_MRR(self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst)
                self.coherent.start_lasing()               
                self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, self.interpulseinterval)       
            self.coherent.stop_lasing()
            print('Completed lasing')
            self.close() # close window
            #Open new window for results
            NewWindow=UploadResults(self.DailyDirectory,self.TimeDirectory,self.Type)
        NewWindow.exec_()
        
        
# After laser calibration run
class UploadResults(QDialog,UploadPowCalResults_ui):
    def __init__(self,DailyDirectory,TimeDirectory,Type):
        QDialog.__init__(self)
        UploadPowCalResults_ui.__init__(self)
        self.setupUi(self)
       
        self.DailyDirectory=DailyDirectory
        self.TimeDirectory=TimeDirectory 
        self.Type=Type
        
        self.BrowseButtonPC.clicked.connect(self.Upload)
        self.PushButtonChannels.clicked.connect(self.PlotChannels)
        self.closeFigure.clicked.connect(self.closefigure)
        
        self.AnalyseButton.clicked.connect(self.analyseCalData)
        
        
    def Upload(self):
        results_fname,_filter1=QFileDialog.getOpenFileName(self, 'Upload File')
        if self.Type=='Power':                       
            newPath=shutil.copy(results_fname,self.TimeDirectory + '\\' + 'power_calibration_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr')            
        elif self.Type=='MRR':
            newPath=shutil.copy(results_fname,self.TimeDirectory + '\\' + 'MRR_calibration_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr')
        
        self.lineEditDir.setText(newPath)      
        self.AnalyseButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AnalyseButton.setIcon(icon)
        
    def loadEphysData(self):
        '''
        This function assumes one segment with 3 AnalogSignals
        1 - analogsignals[0] is assumed to be picker power
        2 - analogsignals[1] is assumed to be membrane voltage
        3 - analogsignals[2] is assumed to be membrane current

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
        FileName=self.lineEditDir.text()
        ephys=f.load_ephys(FileName) #load using python-neo
        # data
        picker = ephys.segments[0].analogsignals[0][:,1] #this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.
        Vm = ephys.segments[0].analogsignals[1][:,1] #units of mW
        Im = ephys.segments[0].analogsignals[2][:,1] #units of nA   
        Vm_units=Vm.units
        Im_units=Im.units
        Im_Hz=Vm.sampling_rate #same as Vm sampling rate
        picker_Hz=picker.sampling_rate
        
        return ephys,picker,Vm,Im,Vm_units,Im_units, Im_Hz, picker_Hz
    
    def PlotChannels(self):
        ephys,picker,Vm,Im,Vm_units,Im_units, Im_Hz, picker_Hz=self.loadEphysData()
        # plot the data
        plt.figure(1,figsize=(20,15))
        f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
            'Picker power meter (measurement output) voltage vs time',None,311,show=False)
        f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],312,show=False)     
        f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],313,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 1- Plot of Ephys Channels.png')
        plt.show()
        
    
    def closefigure(self):
        plt.close(fig=1)

    # def plot_calibration(self):
    #     calibration_fname,_filter=QFileDialog.getOpenFileName(self, 'Select File')
    #     #plot the calibration
    #     f.plot_data(sample_power_calibration[0,:],sample_power_calibration[1,:],'Picker power (mW)','Power onto cell (mW)',\
    #                 'Calibration curve: Power onto cell vs Picker power',None)
    #     plt.savefig(self.TimeDirectory + '//Figure 2- Plot of Power onto cell vs Picker Power.png')
    #     plt.show()

    # def plotEnergyVsPicker(self): 
    #     #These two constants allow you to convert the voltage measured at the picker 
    #     #into a mW value measured at the picker. The power meter outputs between 0 and picker_max_output Volts
    #     #in direct proportion to the input power as a fraction of picker_max_measurement_mW.
    #     #i.e. if the Picker outputs 1 V, it is measuring 250 mA of current.
    #     picker_max_output_V = 2
    #     picker_max_measurement_mW = 500
    #     beam_spot_diameter = 8 #in micro meters

    #     #this next variable is an array with times and labels which tells us when the calibration and stimulation occurred.
    #     #The label key is in the following dict:
    #     #The keys are loaded as bytes and need to be recovered as characters using the built in chr() function after converting from byte to int
    #     label_key = {'A':'cancel','F':'calibrate','E':'stimulate'}
    #     keyboard = ephys.segments[0].events[1]
    #     labels = [chr(int(x)) for x in keyboard.labels]
        
    #     #command energies
    #     energy=0.5  
    #     duration=5 
    #     # for i in range(self.steps):
    #         #     print(self.energy_as_frac*(i+1))
        
    #     # extract values where picker is maximum
    #     differentiated=np.diff(np.squeeze(picker)) #shows where increasing and decreasing
    #     indexes=np.where(differentiated>0)#these give the indexes of increasing
    #     picker_squeeze=np.squeeze(picker)
    #     indexes_only=picker_squeeze[indexes] #extract only powers of indexes
    #     thres=np.where(indexes_only>0.05) #now apply a threshold
        
        
        
    #     time_increment=1/sampling_rate
    #     start_sample=start_time*frequency
        
        
        


        
# Terms of use pop-up box
class TermsOfUse(QDialog):
    def __init__(self):
        super(TermsOfUse,self).__init__()
        uic.loadUi('TermsOfUse.ui',self)
        
        self.TrainingButton.clicked.connect(self.OpenLaserTraining)
        self.LaserManualButton.clicked.connect(self.OpenLaserManual)
        self.ReportButton.clicked.connect(self.OpenReport)
    
    def OpenLaserTraining(self):
        path=r'http://www.imperial.ac.uk/safety/safety-by-topic/laboratory-safety/laser-safety/lasersafetytraining/'
        webbrowser.open(path)
    
    def OpenLaserManual(self):
        path=r'https://edge.coherent.com/assets/pdf/COHR_Monaco1035_DS_0120_1.pdf'
        webbrowser.open(path)
    
    def OpenReport(self):
        path=r'https://github.com/AliSan123/Optogenetics_project'
        webbrowser.open(path)



#############################################################################
if __name__ == "__main__":
    arduino=Arduino.Arduino('COM3',9600) #open the port
    coherent=Coherent.Coherent('COM1',19200,test=True)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui(arduino,coherent)
    window.show()

    sys.exit(app.exec_())
    arduino.close_port()
    coherent.close_port()


