# Author:           Alison Sanders
# Last edited:      09/08/2020

import serial 

class Arduino:
    '''
    This class controls a Arduino microcontroller via RS-232 serial commands.
    The Coherent laser is in Gated mode, looking for the TTL HIGH signal to deploy the pulses.
    This TTL signal is tightly controlled for timing and so requires the Arduino MC for control.
    This class can:
    - Open the serial port to Arduino MC
    - Sets duration of TTL ON/ OFF (calibration/ stimulaion time)
    - Sets the inter-trial interval (ITI)/ time between pulses
    '''
    def __init__(self, arduino_port,baudrate):
        #initialise a serial port (name of port, baudrate).
        self.baudrate=baudrate
        self.arduino_port = serial.Serial(arduino_port,baudrate) # open and close port later
        
    def TTL_sequence(self,pulse_duration_ms,time_betw_pulses_ms,n_times):
        '''
        This function defines the pulse sequence.
        1) TTL on for pulse_duration
        2) TTL off for time_betw_pulses_ms
        3) On and Off repeated n_times
        '''

        for i in range(n_times):
            self.__write__('HI'+ str(pulse_duration_ms)) # Send HI ('HIGH'='ON'); integer in milliseconds
            self.__readline__() # Read the serial message response
            
            self.__write__('LO'+ str(time_betw_pulses_ms)) # Send an L ('LOW'='OFF')
            self.__readline__() # Read response  
            
        self.arduino_port.close()
        
    def __write__(self,command):
        '''
        This function writes a serial command and prints what is sent to screen.
        comman: (str) serial command to be sent     
        '''
        self.arduino_port.write(command.encode('utf-8'))
        print(f'Sent: {command}')

    def __readline__(self):
        '''
        This function reads the serial message and prints message to screen.
        '''
        ans=self.arduino_port.readline() #read serial message
        msg=ans.decode('utf-8') #prints serial message to screen
        return msg  

arduino=Arduino('COM3',9600)
arduino.TTL_sequence(pulse_duration_ms=250,time_betw_pulses_ms=500,n_times=10)

