# Author:           Alison Sanders
# Date created:     30/06/2020
# Last edited:      09/08/2020


import serial 

import os
path=r'C:\Users\user\Desktop\2019 - MSc\Project\Scripts\Optogenetics_project'
os.chdir(path)

class Coherent:
    '''
    This class controls a Coherent Monaco laser using RS-232 serial commands.
    - Opens the serial port
    - Sets all parameters, including repetition rate and energy 
    - Starts up laser 
    '''
    
    def __init__(self,serial_port,baudrate,virtual=True): 
        self.serial_port=serial_port
        self.virtual=virtual 
        self.baudrate=baudrate #factory settings 19200 are default (Manual page 6-6)
        
        #self.keyswitch_position=keyswitch_position
        #self.MRR=MRR
        #self.PW=PW
        #self.RRDivisor=RRDivisor
        #self.PulsesPerMBurst=PulsesPerMBurst 
        #self.energy=energy
        
        if virtual: #testing
            self.serial_port=open('./virtual_port.txt','w')
        else:
            self.serial_port=serial.Serial(serial_port,baudrate)
            self.__readline__()           
   
    def startup(self,keyswitch_position):
        """
        This function checks the keyswitch is on, declares pulse mode and checks for warnings and faults.
        
        """        
        #Check keyswitch is on
        self.__write__('?K')
        if self.__readline__()==1:     #If the keyswitch is on:
             print('Keyswitch is Enabled. Laser is starting up from standby.')
             # Declare pulse mode, n=1 for Gated mode (p6-12)
             self.__write__('PM=1')
             
             #Check for warnings and faults
             self.__write__('?F')
             print(self.__readline__())         
        else:
             print('Keyswitch is off. Set keyswitch to the <ENABLE> position')

                
    def set_MRR(self):
        """
        This function sets the command repetition rate. This will be called upon and varied often during experiment.
        
        """        
        self.__write__('SET={self.MRR},{self.PW},{self.RRDivisor},{self.PulsesPerMBurst}') # Declare initial parameters (p6-14)
    
    
    def set_energy(self):
        """
        This function sets the command energy level (0-100% of 40J). This will be called upon and varied often during experiment.
        
        """         
        self.__write__('RL={self.energy}')
        
    
    def start_lasing():
        """
        This function sends the commands to laser to turn on and start pulsing
        
        """  
        write_command(self,'S=1')         # Open Shutter, shutter indicator will light on the power supply front panel
   
        write_command(self,'PC=1')        # Turn on pulses
    
        write_command(self,'L=1')         # Turn on diodes - they will ramp to set current in ~30s, allow >45 min to achieve operating temperature

    def __write__(self,command):
        '''
        This function writes a serial command and prints what is sent to screen.
        comman: (str) serial command to be sent     
        '''
        self.serial_port.write(command.encode('utf-8'))
        print(f'Sent: {command}')

    def __readline__(self):
        '''
        This function reads the serial message and prints message to screen.
        '''
        ans=self.serial_port.readline() #read serial message
        msg=ans.decode('utf-8') #prints serial message to screen
        return msg  
        