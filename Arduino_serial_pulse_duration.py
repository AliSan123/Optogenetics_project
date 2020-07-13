#Import serial control module
#read the docs at https://pyserial.readthedocs.io/en/latest/shortintro.html
import serial
import time

#initialise a serial port (name of port, baud rate). The name will likely be different on your computer
ser = serial.Serial('COM3',9600)

#read initial serial message
answer = ser.readline()
print(answer.decode('utf-8'))


#turn LED on and off once

LED_status = 1
command = str(LED_status) # converts to string
print(f'Sent: {command}')
ser.write(command.encode('utf-8'))
response = ser.readline()
print(f'Response: {response.decode("utf-8")}')
time.sleep(0.05) # on for 5ms

LED_status = 0
command = str(LED_status) # converts to string
print(f'Sent: {command}')
ser.write(command.encode('utf-8'))
response = ser.readline()
print(f'Response: {response.decode("utf-8")}')

# python will tell LED to turn on for exposire time
# upload sketch once
# initialisation procedures
# one function gets called over and over - function accepts exposure time and cause arduino to pulse on LED once and hen stop
# serial inputs to laser directly - lser commands
# python code sleep for certain amount of time (5 s -1 min (inter trial interval))
# loop