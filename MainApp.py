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
import numpy as np
import shutil
import Coherent
import Arduino
import functions as f
import matplotlib.pyplot as plt
import pyqtgraph as pg


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
        self.RunButton.clicked.connect(self.OpenSafetyWindow)
     
#       Cell Experiments
        self.energy_radio.clicked.connect(self.toggle_radio)
        self.MRR_radio.clicked.connect(self.toggle_radio)
        self.step_intervals.clicked.connect(self.toggle_radio)
        self.custom_list.clicked.connect(self.toggle_radio)
        self.setCellParams.clicked.connect(self.getCellParamVals)    
        
        
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
    def OpenSafetyWindow(self): 
        MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement,beam_diameter=self.getParamVals()
        TimeDirectory=self.getTimeDirectory()
        DailyDirectory=self.getDailyDirectory()
        SW=SafetyWindow(self.arduino,self.coherent,DailyDirectory,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement,beam_diameter)
        SW.exec_()
        
    def getParamVals(self):
        #Fixed params
        pulse_duration_ms=self.CalTimeSpinBox.value() 
        beam_diameter=self.BeamDiamSpinBBox.value()
        interpulseinterval=self.IPISpinBBox.value()
        picker_max_output=self.picker_max_output.value()
        picker_max_measurement=self.picker_max_measurement.value()       
        combo_txt=self.comboBox.currentText()
        combo_lst=combo_txt.split(",")
        MRR_in_kHz=combo_lst[0]
        PW_in_fs=combo_lst[1]
        RRDivisor=combo_lst[2]
        PulsesPerMBurst=combo_lst[3]
        # Variable (energy) params
        min_energy_as_frac=self.energy_spinbox.value()/100
        print('min energy as frac= %2f'%min_energy_as_frac)
        max_energy_as_frac=self.energy_spinbox_2.value()/100
        print('max energy as frac= %2f'%max_energy_as_frac)
        steps=self.energy_spinbox_3.value() #how many energy values do you want to test?
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
 
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,pulse_duration_ms,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement,beam_diameter
              
    def RunButtonToGreen(self):
        self.RunButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RunButton.setIcon(icon)
        
# Cell Experiments
    def toggle_radio(self):
        if self.energy_radio.isChecked():
           #change style sheet
           self.energy_title.setStyleSheet("background-color: rgba(0, 153, 255, 50)")
           if self.step_intervals.isChecked():
               self.min_energy_spin.setStyleSheet("")
               self.min_energy_spin.setReadOnly(False)
               self.max_energy_spin.setStyleSheet("")
               self.max_energy_spin.setReadOnly(False)
               self.energy_steps.setStyleSheet("")
               self.energy_steps.setReadOnly(False)
           elif self.custom_list.isChecked():
               self.custom_list_combo.setStyleSheet("")
               self.custom_list_combo.setEditable(True)
               
        elif self.MRR_radio.isChecked():
            self.MRR_heading.setStyleSheet("background-color: rgba(0, 153, 255, 50)")
            self.MRRcomboBox_2.setStyleSheet("")
            self.MRRcomboBox_2.setEditable(True)
            
            
    def getCellParamVals(self):
        exp_label=self.exp_label.text()
        pulse_duration_ms=self.pulse_duration.value()
        beam_diameter=self.BeamDiamSpinBBox_3.value()
        PW_in_fs=self.PWdoubleSpinBox_2.value()
        RRDivisor=self.lineEdit_3.text()
        PulsesPerMBurst=self.lineEdit_4.text() 
        n_times=self.n_times_spinbox.value()
        
        
class SafetyWindow(QDialog,SafetyWindow_ui):
    def __init__(self,arduino,coherent,DailyDirectory,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement,beam_diameter):
        QDialog.__init__(self)
        SafetyWindow_ui.__init__(self)
        self.setupUi(self)
      
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
        self.picker_max_output=picker_max_output
        self.picker_max_measurement=picker_max_measurement
        self.beam_diameter=beam_diameter
        
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
        self.coherent.startup() #start laser from standby - checks and Pulse Mode=1
        self.coherent.set_MRR(self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst) #set parameters
        energy_list=[]
        # the following increases the energy % sent with each loop with the 
        # option to repeat an energy level n_times
        for i in range(int(self.steps)):               
            self.energy_as_frac*(i)
            print('Energy sent is: '+ self.energy_as_frac*(i))
            self.coherent.set_energy(self.energy_as_frac*(i))
            self.coherent.start_lasing()
            self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, self.interpulseinterval)               
            energy_list.append(np.repeat(self.energy_as_frac*(i),self.n_times))                
        self.coherent.stop_lasing()
        print('Completed lasing Power')
        self.close() # close window
        #Open new window for results
        NewWindow=UploadResults(self.DailyDirectory,self.TimeDirectory,energy_list)
        NewWindow.exec_()     

 

# After laser calibration run
class UploadResults(QDialog,UploadPowCalResults_ui):
    def __init__(self,DailyDirectory,TimeDirectory,energy_list):
        QDialog.__init__(self)
        UploadPowCalResults_ui.__init__(self)
        self.setupUi(self)
       
        self.DailyDirectory=DailyDirectory
        self.TimeDirectory=TimeDirectory 
        self.energy_list=energy_list # energy or MRR depending on Type
        
        self.BrowseButtonPC.clicked.connect(self.Upload)
        self.PushButtonChannels.clicked.connect(self.PlotChannels)
        self.closeFigure.clicked.connect(self.closefigure)
        
        #self.AnalyseButton.clicked.connect(self.analyseCalData)
        
        
    def Upload(self):
        results_fname,_filter1=QFileDialog.getOpenFileName(self, 'Upload File')
        newPath=shutil.copy(results_fname,self.TimeDirectory + '\\' + 'power_calibration_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr')
        self.lineEditDir.setText(newPath)      
        self.AnalyseButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AnalyseButton.setIcon(icon)
    
    def PlotChannels(self):
        ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=f.loadEphysData(self.lineEditDir.text())
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


