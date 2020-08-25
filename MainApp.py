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
import numpy as np
import shutil
import Coherent
import Arduino
import functions as f
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import pyqtgraph as pg
import pyqtgraph.exporters


SafetyWindow_ui,_=uic.loadUiType('SafetyWindow.ui')
UploadCalResults_ui,_=uic.loadUiType('UploadCalResults.ui')
UploadPart1Results_ui,_=uic.loadUiType('UploadPart1Results.ui')

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
        self.PushButtonCalibration.clicked.connect(self.PlotCalibration)
        self.closeFigure_2.clicked.connect(lambda: self.closefigure(1))
        self.NextButton.clicked.connect(self.GoToPowerCalibration)

#       POWER CALIBRATION TAB            
        self.setParams.clicked.connect(self.getParamVals) 
        self.setParams.clicked.connect(lambda: self.RunButtonToGreen(button=self.RunButton))
        self.RunButton.clicked.connect(lambda: self.OpenSafetyWindow('calibration'))
     
#       Cell Experiments Part 1 - Kd
        self.setCellParams.clicked.connect(self.getCellParamVals)   
        self.setCellParams.clicked.connect(lambda: self.RunButtonToGreen(button=self.RunButton_3))
        self.RunButton_3.clicked.connect(lambda: self.OpenSafetyWindow('cells_KD'))

#       Cell Experiments Part 2 - Optimisation
        

        
#       HOME SCREEN  
    def OpenTermsOfUse(self):
        TOU=TermsOfUse()
        TOU.exec_()

    def closefigure(self,figure):
        plt.close(fig=figure)

    def PlotCalibration(self):
        CalibrationFile=self.lineEditFile.text()
        power_calibration=np.loadtxt(CalibrationFile)
        #plot the calibration
        plt.figure(1,figsize=(15,10))
        power_onto_cell_mW=power_calibration[1,:]
        cal_picker_power_mW=power_calibration[0,:]
        f.plot_data(cal_picker_power_mW,power_onto_cell_mW,'Picker power (mW)','Power onto cell (mW)',\
                    'Calibration curve: Power onto cell vs Picker power',None,111,show=False)
        plt.savefig(self.getDailyDirectory() + '//Plot of Power onto cell vs Picker Power.png')
        plt.show()
    
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
        newPath=shutil.copy(calibration_fname,self.getDailyDirectory() + '\\' + 'power_calibration_980nm_8um_spot -' + datetime.datetime.now().strftime('%Y-%m-%d') + '.dat')
        self.lineEditFile.setText(newPath)      
        self.NextButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NextButton.setIcon(icon) 
    
    
    def GoToPowerCalibration(self):
        self.tabWidget.setCurrentIndex(2)

#       POWER CALIBRATION
    def OpenSafetyWindow(self,section): 
        if section=='calibration':
            pulse_duration_ms,beam_diameter,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement=self.getParamVals()
            exp_label='cal'# not ued but need to set to pass into class
        elif section == 'cells_KD':
            exp_label,pulse_duration_ms,beam_diameter,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps=self.getCellParamVals()
            # the following aren't used but are just set so they can be passed into the next class
            picker_max_output=500
            picker_max_measurement=2
        TimeDirectory=self.getTimeDirectory()
        DailyDirectory=self.getDailyDirectory()
        CalibrationFile=self.lineEditFile.text()
        print(section)
        SW=SafetyWindow(self.arduino,self.coherent,section,DailyDirectory,TimeDirectory,CalibrationFile,pulse_duration_ms,beam_diameter,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement,exp_label)
        SW.exec_()
        self.tabWidget.setCurrentIndex(3)
        
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
        max_energy_as_frac=self.energy_spinbox_2.value()/100
        steps=self.energy_spinbox_3.value() #how many energy values do you want to test?
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.energy_spinbox_4.value()
 
        return pulse_duration_ms,beam_diameter,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps,picker_max_output,picker_max_measurement
              
    def RunButtonToGreen(self,button):       
        button.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button.setIcon(icon)
        
# Cell Experiments - Constant
      
    def getCellParamVals(self):
        # Fixed values
        exp_label=self.exp_label.text()
        pulse_duration_ms=self.pulse_duration.value()
        interpulseinterval=self.IPISpinBBox_2.value()
        beam_diameter=self.BeamDiamSpinBBox_3.value()
        MRR=self.MRR_lineEdit.text()
        PW_in_fs=self.PWdoubleSpinBox_2.value()
        RRDivisor=self.lineEdit_3.text()
        PulsesPerMBurst=self.lineEdit_4.text() 
        # Variable values
        min_energy_as_frac=self.energy_spinbox_min.value()/100
        max_energy_as_frac=self.energy_spinbox_max.value()/100
        steps=self.steps_spinBox.value() #how many energy values do you want to test?
        delta_energy=(max_energy_as_frac-min_energy_as_frac)/steps #"delta" -change in energy with each ramp up
        n_times=self.n_samples_spinBox.value()
        return exp_label,pulse_duration_ms,beam_diameter,MRR,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps

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


        
class SafetyWindow(QDialog,SafetyWindow_ui):
    def __init__(self,arduino,coherent,section,DailyDirectory,TimeDirectory,CalibrationFile,pulse_duration_ms,beam_diameter,MRR_in_kHz,PW_in_fs,RRDivisor,PulsesPerMBurst,delta_energy,n_times,interpulseinterval,steps,picker_max_output=500,picker_max_measurement=2,exp_label='exp'):
        QDialog.__init__(self)
        SafetyWindow_ui.__init__(self)
        self.setupUi(self)
      
        self.arduino=arduino
        self.coherent=coherent
        self.section=section
        self.TimeDirectory=TimeDirectory
        self.DailyDirectory=DailyDirectory
        self.CalibrationFile=CalibrationFile
        
        self.MRR_in_kHz=MRR_in_kHz
        self.PW_in_fs=PW_in_fs
        self.RRDivisor=RRDivisor
        self.PulsesPerMBurst=PulsesPerMBurst
        self.delta_energy=delta_energy
        self.pulse_duration_ms=pulse_duration_ms
        self.n_times=n_times
        self.steps=steps   
        self.interpulseinterval=interpulseinterval          
        self.picker_max_output=picker_max_output
        self.picker_max_measurement=picker_max_measurement
        self.beam_diameter=beam_diameter    
        self.exp_label=exp_label
       
        self.checkBoxKeyswitch.stateChanged.connect(self.ChangeColour)
        self.LaserManualButton2.clicked.connect(self.OpenLaserManual) 
        self.SWRunButton.clicked.connect(self.StartLaser)           
        
        
        
    def ChangeColour(self):          
        if self.checkBoxIsSafe.isChecked() and self.checkBoxKeyswitch.isChecked():
            self.SWRunButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.SWRunButton.setIcon(icon)
    
    def OpenLaserManual(self):
        path=r'https://edge.coherent.com/assets/pdf/COHR_Monaco1035_DS_0120_1.pdf'
        webbrowser.open(path)
        
    def getEnergyList(self):
        energy_list=[]
        for i in range(int(self.steps)):
            energy_list.append(np.repeat(self.delta_energy*(i),self.n_times))
        energy_list=np.asarray(energy_list).flatten()
        # for the cell experiments, we want to randomise the powers
        if self.section=='cells_KD':
            print(energy_list)
            np.random.shuffle(energy_list)  
            print(energy_list)
        return energy_list
    
    def StartLaser(self):
        self.coherent.startup() #start laser from standby - checks and Pulse Mode=1
        self.coherent.set_MRR(self.MRR_in_kHz,self.PW_in_fs,self.RRDivisor,self.PulsesPerMBurst) #set parameters
        energy_list=self.getEnergyList()
        # the following increases the energy % sent with each loop with the 
        # option to repeat an energy level n_times
        for energy in energy_list:               
            print(energy)
            self.coherent.set_energy(energy)
            self.coherent.start_lasing()
            self.arduino.TTL_sequence(self.pulse_duration_ms, self.n_times, self.interpulseinterval)                                          
        self.coherent.stop_lasing()
        print('Completed lasing')
        self.close() # close window
        
        #Open new window for results
        if self.section=='calibration':
            NewWindow=UploadCalResults(self.DailyDirectory,self.TimeDirectory,self.CalibrationFile,energy_list,self.pulse_duration_ms,self.picker_max_output,self.picker_max_measurement,self.beam_diameter)
            NewWindow.exec_()     
        elif self.section=='cells_KD':
            DiffWindow=UploadPart1Results(self.DailyDirectory,self.TimeDirectory,energy_list,self.pulse_duration_ms,self.beam_diameter)
            DiffWindow.exec_()
        

# After laser calibration run
class UploadCalResults(QDialog,UploadCalResults_ui):
    def __init__(self,DailyDirectory,TimeDirectory,CalibrationFile,energy_list,pulse_duration_ms,picker_max_output_V,picker_max_measurement_mW,beam_diameter):
        QDialog.__init__(self)
        UploadCalResults_ui.__init__(self)
        self.setupUi(self)
       
        self.DailyDirectory=DailyDirectory
        self.TimeDirectory=TimeDirectory 
        self.CalibrationFile=CalibrationFile
        self.energy_list=energy_list 
        self.pulse_duration_ms=pulse_duration_ms
        self.picker_max_output_V=picker_max_output_V
        self.picker_max_measurement_mW=picker_max_measurement_mW
        self.beam_diameter=beam_diameter

        
        self.BrowseButtonPC.clicked.connect(self.Upload)
        self.PushButtonChannels.clicked.connect(self.PlotChannels)
        self.closeFigure.clicked.connect(lambda: self.closefigure(1))
        

        self.AnalyseButton.clicked.connect(self.analyseCalibration)
        
        
    def Upload(self):
        results_fname,_filter1=QFileDialog.getOpenFileName(self, 'Upload File')
        newPath=shutil.copy(results_fname,self.TimeDirectory + '\\' + 'power_calibration_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr')
        self.lineEditDir.setText(newPath)      
        self.AnalyseButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AnalyseButton.setIcon(icon)
    
    
    # def PlotChannels(self):
    #     ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=f.loadEphysData(self.lineEditDir.text())        
    #     plot=pg.PlotWidget()
    #     window=pg.PlotWidget()
    #     window.plot(picker.times,np.squeeze(picker))
    #     exporter=pg.exporters.ImageExporter(window.plotItem)
    #     exporter.export(self.TimeDirectory + '//Figure 1- Plot of Ephys Channels.png')
    def PlotChannels(self):
        ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=f.loadEphysData(self.lineEditDir.text())
        # plot the data
        plt.figure(1,figsize=(20,15))
        f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
            'Picker power meter (measurement output) voltage vs time',None,311,show=False)
        f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],312,show=False)     
        f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],313,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 1- Plot of Ephys Channels (calibration).png')
        plt.show()    
    


    def analyseCalibration(self):
        ephysfile=self.lineEditDir.text() #ephys .smr file
        mean_picker_volts=f.GetMeanVolts(ephysfile,self.pulse_duration_ms,self.energy_list,dead_time=2,test=True)
        plt.figure(2,figsize=(15,10))
        f.plot_data(self.energy_list,mean_picker_volts,'Input RL energy (%)','Mean Picker volts (V))',\
                    'Calibration curve: Mean Picker Volts versus Input RL energy',None,111,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 2- Plot of Mean Picker Volts versus Input RL energy.png')
        plt.show()
        
        plt.figure(3,figsize=(15,10))
        Power_density=f.convert_V_W(mean_picker_volts,self.picker_max_measurement_mW,self.picker_max_output_V,self.CalibrationFile,self.beam_diameter)
        
        f.plot_data(self.energy_list,Power_density,'Input RL energy (%)','Mean Power Density in sample (mW/um2))',\
                    'Calibration curve: Mean Power Density in sample versus Input RL energy',None,111,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 3- Plot of Mean Power Density in sample versus Input RL energy.png')
        plt.show()
        
        data={'energy_list':self.energy_list, 'mean_picker_volts':mean_picker_volts, 'Power_density':Power_density}
        results=pd.DataFrame(data=data)
        results.to_csv(self.TimeDirectory + '//Mean power density in sample vs energy list.csv')
        #Once saved, close window and go to next tab
        self.close()
        
# After Cell experiments Part 1  run
class UploadPart1Results(QDialog,UploadPart1Results_ui):
    def __init__(self,DailyDirectory,TimeDirectory,energy_list,pulse_duration_ms,beam_diameter):
        QDialog.__init__(self)
        UploadPart1Results_ui.__init__(self)
        self.setupUi(self)
    
        self.DailyDirectory=DailyDirectory
        self.TimeDirectory=TimeDirectory 
        self.energy_list=energy_list 
        self.pulse_duration_ms=pulse_duration_ms
        self.beam_diameter=beam_diameter
    
        self.BrowseButtonPC.clicked.connect(self.Upload)
        self.PushButtonChannels.clicked.connect(self.PlotChannels)
        self.closeFigure.clicked.connect(lambda: self.closefigure(1))
        
        self.AnalyseButton.clicked.connect(self.analyse)
        
    def PlotChannels(self):
        ephys,picker,Vm,Im,picker_units,Vm_units,Im_units,Vm_Hz, Im_Hz, picker_Hz=f.loadEphysData(self.lineEditDir.text())
        # plot the data
        plt.figure(1,figsize=(20,15))
        f.plot_data(picker.times,np.squeeze(picker),'Time (s)','Picker power meter\nmeasurement output (V)',\
            'Picker power meter (measurement output) voltage vs time',None,311,show=False)
        f.plot_data(Vm.times,np.squeeze(Vm),None,f'Membrane Voltage\n({Vm.units})','Membrane voltage vs time',[-50,-10],312,show=False)     
        f.plot_data(Im.times,np.squeeze(Im),None,f'Membrane Current\n({Im.units})','Membrane current vs time',[-1,1],313,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 5- Plot of Ephys Channels (Part 1).png')
        plt.show()   
        
    def Upload(self):
        results_fname,_filter1=QFileDialog.getOpenFileName(self, 'Upload File')
        newPath=shutil.copy(results_fname,self.TimeDirectory + '\\' + 'cell_exp_1_results -' + datetime.datetime.now().strftime('%Hh%Mm%Ss') + '.smr')
        self.lineEditDir.setText(newPath)      
        self.AnalyseButton.setStyleSheet("font: 14pt \"Eras Bold ITC\"; color: rgb(0, 170, 0)")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/QTIcons/RunArrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AnalyseButton.setIcon(icon)
       
    def analyse(self):
        ephysfile=self.lineEditDir.text() #ephys .smr file
        min_current_vals=f.GetCurrent(ephysfile,self.pulse_duration_ms,self.energy_list,divisor=50,dead_time=2,test=True)
        plt.figure(4,figsize=(15,10))
        f.plot_data(self.energy_list,min_current_vals,'Input RL energy (%)','Minimum (averaged) Membrane Current (nA))',\
                    'Calibration curve: Minimum (averaged) Membrane Current versus Input RL energy',None,111,show=False)
        plt.savefig(self.TimeDirectory + '//Figure 2- Plot of Minimum (averaged) Membrane Current versus Input RL energy.png')
        plt.show()
        
        cal_results=pd.read_csv(self.TimeDirectory + '//Mean power density in sample vs energy list.csv')
        x_data=cal_results['energy_list']
        y_data=cal_results['Power_density']
        #interpolation function which will be used to get the power at a given energy value
        interpld=interp1d(x_data,y_data) 
        new_Power_Density=interpld(self.energy_list)#This give sinterpolated power vals for experimental energy values 
        current_density=min_current_vals/(np.pi*(self.beam_diameter/2)**2)
        
        data={'energy_list':self.energy_list,'power_density':new_Power_Density,'current_density':current_density, 'min_current_vals':min_current_vals}
        results=pd.DataFrame(data=data)
        results.to_csv(self.TimeDirectory + '// Minimum (averaged) Membrane Current vs Mean Power Density in sample.csv')
        
        #Find Kd - this should be a function
        Kd=f.getKd(new_Power_Density,current_density)
        # Imax=np.max(current_density)
        # I_half_max=Imax/2
        # f2=interp1d(current_density,new_Power_Density)#interpolate x-axis
        # ynew=I_half_max
        # Kd=f2(ynew)
        print('Kd='+str(Kd))
        #Once saved, close window and go to next tab
        self.close()
        
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


