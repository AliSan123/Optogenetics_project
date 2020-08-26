# Author:           Alison Sanders
# Last edited:      09/08/2020

import serial 
import time

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
        self.arduino_port = arduino_port
        self.ser=self.open_port()
        self._readline_() # Read the initial serial message response
        
        
    def TTL_sequence(self,pulse_duration_ms,min_time_off):
        '''
        This function encodes the pulse sequence in the Arduino_sketch.ino.
        TTL on for pulse_duration, confirm command completed, 
        then TTL off for arbitrary time, confirm off
        Variables:
        pulse_duration_ms = the delay timefor which TTL=HIGH
        min_time_off = the minimum time in seconds for which the TTL=LOW before starting loop again. 
                        (minimum because there is error associated with the processing time)
        '''

        self._write_(str(pulse_duration_ms)) # Send integer in milliseconds
        self._readline_() # Read the serial message response
        self._readline_() 
        time.sleep(min_time_off) #this will have a relatively large error associatd with it
            
    def _write_(self,command):
        '''
        This function writes a serial command and prints what is sent to screen.
        comman: (str) serial command to be sent     
        '''
        self.ser.write(command.encode('utf-8'))
        print(f'Sent: {command}')

    def _readline_(self):
        '''
        This function reads the serial message and prints message to screen.
        '''
        ans=self.ser.readline() #read serial message
        msg=ans.decode('utf-8') #prints serial message to screen
        print(msg)
    
    def open_port(self):
        ser=serial.Serial(self.arduino_port,self.baudrate) 
        return ser
    
    def close_port(self):
        self.ser.close()

if __name__=='__main__':        
    arduino=Arduino('COM3',9600) 
    arduino.TTL_sequence(pulse_duration_ms=5000,n_times=3,min_time_off=0)
    arduino.close_port()
