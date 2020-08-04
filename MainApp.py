from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QDialog, QFileDialog
from icons import *
#from tkinter import tk
import sys
import webbrowser

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
        #self.BrowseButton2.clicked.connect(self.UploadCalibrationFile)

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
        dialog=QFileDialog.getExistingDirectory(self,'Open Directory','Project Folder',QFileDialog.ShowDirsOnly)
        self.lineEditDirectory.setText(dialog)
        # create subfolders within this: experiments; daily dates
    
    # def UploadCalibrationFile(self):
#        fileName=QFileDialog.getOpenFileName(self,'Select File','Calibration File','DAT Files (*.dat)')
        # open the file 
        # change directories
        # save the file
    #     self.file_save()
    
    # def file_open(self):
    #     name = QFileDialog.getOpenFileName(self, 'Open File')
    #     file = open(name,'r')
    
    #     self.editor()
    
    #     with file:
    #         text = file.read()
    #         self.textEdit.setText(text)
    
    # def file_save(self):
    #     name = QFileDialog.getSaveFileName(self, 'Save File')
    #     file = open(name,'w')
    #     text = self.textEdit.toPlainText()
    
    #     file.write(text)
    #     file.close()
        # self.lineEditFile.setText(str(fileName))

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