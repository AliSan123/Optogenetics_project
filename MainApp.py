from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog
from icons import *
import sys
import webbrowser
import os
import datetime
import pandas as pd
import numpy as np
import Coherent
import Arduino

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui,self).__init__() #call the inherited classes __init__method
        uic.loadUi('MainApp.ui',self) # Load the .ui file
        
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
        self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst,self.energy_in_percent,self.pulse_duration_ms,self.n_times,self.steps=self.getCalData()
        self.ui=SafetyWindow(self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst,self.energy_in_percent,self.pulse_duration_ms,self.n_times,self.steps)    
        self.RunButton.clicked.connect(self.OpenSafetyWindow)

        
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
        
    def UploadCalibrationFile(self):
        calibration_fname,_filter=QFileDialog.getOpenFileName(self, 'Upload File')
        input_file=np.loadtxt(str(calibration_fname))
        output_df=pd.DataFrame(input_file)
        self.SetDailyDirectory() #change directory to saving location
        Filedirectory='power_calibration_980nm_8um_spot -' + datetime.datetime.now().strftime('%Y-%m-%d') + '.dat'
        output_df.to_csv(Filedirectory)
        self.lineEditFile.setText(os.getcwd() + '\'' + Filedirectory)
        
        self.NextButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NextButton.setIcon(icon)

    def GoToPowerCalibration(self):
        self.tabWidget.setCurrentIndex(2)

#       POWER CALIBRATION
    def OpenSafetyWindow(self):
        SW=SafetyWindow()
        SW.exec_()
    
    def getCalData(self):
        #Repetition rate parameters
        combo_txt=self.comboBox.currentText()
        combo_lst=combo_txt.split(", ")
        MRR_in_kHz=combo_lst[0]
        PW_in_fs=combo_lst[1]
        RRDivisor=combo_lst[2]
        PulsesPerMBurst=combo_lst[3]
        # energy params
        min_energy_in_percent=self.energy_spinbox.value()
        max_energy_in_percent=self.energy_spinbox_2.value()
        steps=self.energy_spinbox_3.value()
        energy_in_percent=(max_energy_in_percent-min_energy_in_percent)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
        
        pulse_duration_ms=self.CalTimeSpinBox.value()
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_in_percent,pulse_duration_ms,n_times,steps
        
class SafetyWindow(QDialog):
    def __init__(self,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_in_percent,pulse_duration_ms,n_times,steps):
        super(SafetyWindow,self).__init__()
        uic.loadUi('SafetyWindow.ui',self)
        
        self.MRR_in_kHz=MRR_in_kHz
        self.PW_in_fs=PW_in_fs
        self.RRDivisor=RRDivisor
        self.PulsesPerMBurst=PulsesPerMBurst
        self.energy_in_percent=energy_in_percent
        self.pulse_duration_ms=pulse_duration_ms
        self.n_times=n_times
        self.steps=steps
        
        self.Coherent=Coherent.Coherent('COM1',9600,False)
        self.Arduino=Arduino.Arduino('COM3',9600)
        
        self.checkBoxKeyswitch.stateChanged.connect(self.ChangeColour)
        self.LaserManualButton2.clicked.connect(self.OpenLaserManual) 
        self.SWRunButton.clicked.connect(self.StartLaserCalibration)
        self.close_ports()
        
    def ChangeColour(self):          
        if self.checkBoxIsSafe.isChecked() and self.checkBoxKeyswitch.isChecked():
            self.SWRunButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.SWRunButton.setIcon(icon)
    
    def OpenLaserManual(self):
        path=r'https://edge.coherent.com/assets/pdf/COHR_Monaco1035_DS_0120_1.pdf'
        webbrowser.open(path)
                  
    def StartLaserCalibration(self,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_in_percent,pulse_duration_ms,n_times,steps):
        self.Coherent.startup()
        self.Coherent.set_MRR(MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst)
        for i in range(steps):
            print(energy_in_percent*(i+1))
            self.Coherent.set_energy(energy_in_percent*(i+1))
            self.Coherent.start_lasing()            
            self.Arduino.TTL_sequence(pulse_duration_ms, n_times, min_time_off=0)
        self.Coherent.stop_lasing()
        
    
    def close_ports(self):
        self.Coherent.close_port()
        self.Arduino.close_port()
        
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
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
window.show()
app.exec_() # Start the application

