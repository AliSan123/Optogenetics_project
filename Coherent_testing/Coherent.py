# Author:           Alison Sanders
# Date created:     30/06/2020
# Last edited:      11/08/2020

import serial 
import time

class Coherent:
    '''
    This class controls a Coherent Monaco laser using RS-232 serial commands.
    - Opens the serial port
    - Sets all parameters, including repetition rate and energy 
    - Starts up laser 
    '''
    
    def __init__(self,serial_port,baudrate,test=True): 
        self.serial_port=serial_port
        self.test=test 
        self.baudrate=baudrate #factory settings 19200 are default (Manual page 6-6)
        
        if test:
            self.serial_port=open('./test.txt','w')
        else:
            self.serial_port=serial.Serial(serial_port,baudrate)
            self.__readline__()           
   
    def startup(self):
        """
        This function checks the keyswitch is on, declares pulse mode and checks for warnings and faults.
        
        """        
        #Turn on the chiller
        self.__write__('CHEN=1') #Enables the chiller several minutes before turning on laser

        if self.test:
            time.sleep(1) 
        else:
            time.sleep(180)#180s = 3 minutes before turning on laser (manual 4-22)
            
        self.__write__('?K') #Check keyswitch is on
        
        if self.test:
            keyswitch=1
        else:
            keyswitch=int(self.__readline__())

        if keyswitch==1:     #If the keyswitch is on:
              print('Keyswitch is Enabled. Laser is starting up from standby.')
              self.__write__('PM=1')# Declare pulse mode, n=1 for Gated mode (p6-12)
              
              #Check for warnings and faults
              self.__write__('?F')
              if not self.test:
                  self.__readline__() 
              self.__write__('?W')
              if not self.test:
                  self.__readline__() 
        else:
              print('Keyswitch is off. Set keyswitch to the <ENABLE> position')

                
    def set_MRR(self,MRR_in_kHz,PW_in_fs,RRDivisor=1,PulsesPerMBurst=1):
        """
        This function sets the command repetition rate. This will be called upon and varied often during experiment.
        
        """        
        self.__write__(f'SET={MRR_in_kHz},{PW_in_fs},{RRDivisor},{PulsesPerMBurst}') # Declare initial parameters (p6-14)
        
        
    def set_energy(self, energy_in_percent):
        """
        This function sets the command energy level (0-100% of 40J). This will be called upon and varied often during experiment.
        
        """         
        self.__write__(f'RL={energy_in_percent}')
                
    
    def start_lasing(self):
        """
        This function sends the commands to laser to turn on and start pulsing
        
        """  
        self.__write__('L=1')   # Turn on diodes - they will ramp to set current in ~30s, allow >45 min to achieve operating temperature
        if not self.test:
            time.sleep(40)
            
        self.__write__('?ST')         
        if not self.test:
            self.__readline__()
                
        self.__write__('PC=1')        # Turn on pulses, no response
        
        self.__write__('S=1')         # Open Shutter, shutter indicator will light on the power supply front panel
    
    def stop_lasing(self):
        self.__write__('S=0')    #Closes the shutter and turns off pulsing
    
    def __write__(self,command):
        '''
        This function writes a serial command and prints what is sent to screen.
        comman: (str) serial command to be sent     
        '''
        if not self.test:
            self.serial_port.write(command.encode('utf-8'))
            print(f'Sent: {command}')
        else:
            self.serial_port.write(command+'\n')

    def __readline__(self):
        '''
        This function reads the serial message and prints message to screen.
        '''
        ans=self.serial_port.readline() #read serial message
        msg=ans.decode('utf-8') #prints serial message to screen
        print(msg)
        return msg
        
    def close_port(self):
        self.serial_port.close()

if __name__=='__main__':

    laser=Coherent('COM3',9600,test=True)
    laser.startup()
    laser.set_MRR(500,50)
    laser.set_energy(0.5)
    laser.start_lasing()
    laser.stop_lasing()
    laser.close_port()