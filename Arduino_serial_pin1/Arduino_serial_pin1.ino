/* Arduino 1 Channel TTL Pulse Generator
 * Optogenetics project
 * Alison Sanders
 * Imperial College London
 * 23/06/2020
 * 
 * Description: A  TTL signal is sent out from the Arduino. The duration of the pulse is set as well as the state of the channel.
 */

  // 1 - Tell Arduino to treat pins as output, open serial port.
void setup() {
TTL1=LED_BUILTIN //Change "LED_BUILTIN" to 1 after testing
pinMode(,OUTPUT); //Tell Arduino to treat pin as output

Serial.begin(9600); //Opens serial port, sets data rate to 9600 bps
while (!Serial); // wait for serial port to connect.
Serial.println("Run TTL_sequence");

  }

 // The Arduino will loop through the following code. It writes the pin as high/low:  
void loop() {
  
if (Serial.available()) //Get the number of bytes (characters) available for reading from the serial port
{
int state = Serial.parseInt();//Looks for the next valid integer in the incoming serial
if (state == 1)
{
digitalWrite(TTL1,HIGH); //Write a HIGH (5V) or a LOW (0V) value to a digital pin.
Serial.println("Command completed TTL1 turned ON"); 
}
if (state == 0)
{
digitalWrite(TTL1,LOW); 
Serial.println("Command completed TTL1 turned OFF"); 
}
}
}
