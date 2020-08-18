arduino.close_port()
coherent.close_port()

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
import functions as fn



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
        return TimeDirectory         
    
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
        return newPath       


    def GoToPowerCalibration(self):
        self.tabWidget.setCurrentIndex(2)

#       POWER CALIBRATION
    def OpenSafetyWindow(self,Type): 
        steps=0 #giving it a value because not applicable for 'MRR'
        if Type=='Power':
            MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps=self.getParamVals()
        elif Type=='MRR':
            MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times=self.getMRRParamVals()
            
        TimeDirectory=self.getTimeDirectory()
        SW=SafetyWindow(self.arduino,self.coherent,Type,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps)
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
        print(min_energy_as_frac)
        max_energy_as_frac=self.energy_spinbox_2.value()/100
        print(max_energy_as_frac)
        steps=self.energy_spinbox_3.value()
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
        print(n_times)
        pulse_duration_ms=self.CalTimeSpinBox.value()        
        print(pulse_duration_ms)
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,pulse_duration_ms,n_times,steps
              
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
        print(MRR_in_kHz)
        PW_in_fs=self.PWdoubleSpinBox.value()
        RRDivisor=1
        PulsesPerMBurst=1
        # energy params
        energy_as_frac=self.energy_spinbox_5.value()/100
        n_times=self.MRR_spinbox.value()
        print(n_times)
        pulse_duration_ms=self.CalTimeSpinBox_2.value()        
        print(pulse_duration_ms)
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times
    
    def RunButtonToGreen2(self):
        self.RunButton_2.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RunButton_2.setIcon(icon)
                    


        
class SafetyWindow(QDialog,SafetyWindow_ui):
    def __init__(self,arduino,coherent,Type,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps=0):
        QDialog.__init__(self)
        SafetyWindow_ui.__init__(self)
        self.setupUi(self)
        
        self.Type=Type
        self.arduino=arduino
        self.coherent=coherent
        self.TimeDirectory=TimeDirectory
        
        self.MRR_in_kHz=MRR_in_kHz
        self.PW_in_fs=PW_in_fs
        self.RRDivisor=RRDivisor
        self.PulsesPerMBurst=PulsesPerMBurst
        self.energy_as_frac=energy_as_frac
        self.pulse_duration_ms=pulse_duration_ms
        self.n_times=n_times
        self.steps=steps             
        
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
                self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, min_time_off=0)
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
                self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, min_time_off=0)       
            self.coherent.stop_lasing()
            print('Completed lasing')
            self.close() # close window
            #Open new window for results
            NewWindow=UploadResults(self.TimeDirectory,self.Type)
        NewWindow.exec_()
        
        
# After laser calibration run
class UploadResults(QDialog,UploadPowCalResults_ui):
    def __init__(self,TimeDirectory,Type):
        QDialog.__init__(self)
        UploadPowCalResults_ui.__init__(self)
        self.setupUi(self)
       
        self.TimeDirectory=TimeDirectory 
        self.Type=Type
        
        self.BrowseButtonPC.clicked.connect(self.Upload)
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
        return newPath
    
    def analyseCalData(self):      
        print('Not written yet.')
        
        
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
# app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
# window = Ui() # Create an instance of our class
# window.show()
# app.exec_() # Start the application

if __name__ == "__main__":
    arduino=Arduino.Arduino('COM3',9600) #open the port
    coherent=Coherent.Coherent('COM1',19200,test=True)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui(arduino,coherent)
    window.show()

    sys.exit(app.exec_())
    arduino.close_port()
    coherent.close_port()


