/* Arduino 1 Channel TTL Pulse Generator
 * Optogenetics project
 * Alison Sanders
 * Imperial College London
 * 23/06/2020
 * 
 * Description: A single TTL signal is sent out from the Arduino. The duration of the pulse is set as well as the state of the channel.
 */
  // 1 - Define pins
int TTL1=LED_BUILTIN; //Change to 1 after testing

  // 2 - Tell Arduino to treat pins as output, open serial port.
void setup() {

pinMode(TTL1,OUTPUT); //Tell Arduino to treat pin as output

Serial.begin(9600); //Opens serial port, sets data rate to 9600 bps
while (!Serial); // wait for serial port to connect.
Serial.println("Input 1 to Turn LED on and 2 to off");

  }

  // 3 - Define the pulse duration (in ms) and number of pulses
  int pulse_duration = 5;

 // The Arduino will loop through the following code. It writes the pin as high/low and waits for the pulse duration:  
void loop() {
  
if (Serial.available()) //Get the number of bytes (characters) available for reading from the serial port
{
int state = Serial.parseInt();//Looks for the next valid integer in the incoming serial
if (state == 1)
{
digitalWrite(TTL1,HIGH); //Write a HIGH (5V) or a LOW (0V) value to a digital pin.
delay(pulse_duration);            // waits for 5 ms
Serial.println("Command completed TTL1 turned ON"); 
}
if (state == 0)
{
digitalWrite(TTL1,LOW); 
Serial.println("Command completed TTL1 turned OFF"); 
}
}
}
