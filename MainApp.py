from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog
from icons_rc import *
import sys
import webbrowser
import os
import datetime
import pandas as pd
import numpy as np
import Coherent
import Arduino
import functions as fn



os.chdir(r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project')

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
    
    def getTimeDirectory(self):
        TimeDirectory=self.lineEditDirectory_4.text()
        return TimeDirectory 
    
    def UploadCalibrationFile(self):
        calibration_fname,_filter=QFileDialog.getOpenFileName(self, 'Upload File')
        input_file=np.loadtxt(str(calibration_fname))
        output_df=pd.DataFrame(input_file)
        self.SetDailyDirectory() #change directory to saving location
        Filedirectory='power_calibration_980nm_8um_spot -' + datetime.datetime.now().strftime('%Y-%m-%d') + '.dat'
        output_df.to_csv(Filedirectory)
        self.lineEditFile.setText(os.getcwd() + '\\' + Filedirectory)
        
        self.NextButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NextButton.setIcon(icon)

    def GoToPowerCalibration(self):
        self.tabWidget.setCurrentIndex(2)

#       POWER CALIBRATION
    def OpenSafetyWindow(self): 
        MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps=self.getParamVals()
        TimeDirectory=self.getTimeDirectory()
        SW=SafetyWindow(self.arduino,self.coherent,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps)
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
        min_energy_as_frac=self.energy_spinbox.value()
        print(min_energy_as_frac)
        max_energy_as_frac=self.energy_spinbox_2.value()
        print(max_energy_as_frac)
        steps=self.energy_spinbox_3.value()
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
        print(n_times)
        pulse_duration_ms=self.CalTimeSpinBox.value()        
        print(pulse_duration_ms)
        return MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,pulse_duration_ms,n_times,steps
              
        
        
        
class SafetyWindow(QDialog,SafetyWindow_ui):
    def __init__(self,arduino,coherent,TimeDirectory,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,energy_as_frac,pulse_duration_ms,n_times,steps):
        QDialog.__init__(self)
        SafetyWindow_ui.__init__(self)
        self.setupUi(self)
        
        
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
        NewWindow=UploadPowCalResults(self.TimeDirectory)
        NewWindow.exec_()
        
        
# After laser calibration run
class UploadPowCalResults(QDialog,UploadPowCalResults_ui):
    def __init__(self,TimeDirectory):
        QDialog.__init__(self)
        UploadPowCalResults_ui.__init__(self)
        self.setupUi(self)
       
        self.TimeDirectory=TimeDirectory       
        self.BrowseButtonPC.clicked.connect(self.UploadPowCalResults)
        self.AnalyseButton.clicked.connect(self.analyseCalData)
        
        
    def UploadPowCalResults(self):
        results_fname,_filter1=QFileDialog.getOpenFileName(self, 'Upload File')
        input_file=fn.load_ephys(results_fname) #load file 
        output_df=pd.DataFrame(np.squeeze(ephys.segments[0].analogsignals[0]))
        os.chdir(self.TimeDirectory)#change directory to saving location
        FileName='power_calibration_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr'
        output_df.to_csv(FileName)
        self.lineEditDir.setText(os.getcwd() + '\\' + FileName)
        Filedirectory=os.getcwd() + '\\' + FileName
        self.AnalyseButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AnalyseButton.setIcon(icon)
        return Filedirectory
    
    def analyseCalData(self):
        '''
        Filepath - Path to the .smr file that was uploaded with "UploadPowCalResults"
            
        '''       
        FilePath=self.UploadPowCalResults()
        ephys=fn.load_ephys(FilePath) #load file        
        picker = ephys.segments[0].analogsignals[0][:,1] #this channel shows the power measurement from a beam sampler, proportional to the actual laser power in the system.

        f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],411,show=True)
        f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],412,show=True)
        f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
            'Picker power meter (measurement output) voltage vs time',None,414)


        #plot the figure, save to png in folder, display png?
        
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


