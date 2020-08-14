void setup() {
  // put your setup code here, to run once:
pinMode(LED_BUILTIN,OUTPUT);

Serial.begin(9600);
while (!Serial);
Serial.println("Ready for commands.");
}

void loop() {
  // put your main code here, to run repeatedly:
if (Serial.available())
{
String chiller = Serial.readString();
Serial.println(chiller);

String Keyswitch = Serial.readString();

if (Keyswitch == "?K")
{
  Serial.println(1);
}
String PM = Serial.readString();
if (PM == "PM=1")
{
Serial.println("Confirming Pulse Mode=1");
}
String faults = Serial.readString();
  Serial.println("SYSTEM OK");

String warnings = Serial.readString();
  Serial.println("SYSTEM OK");

String MRR = Serial.readString();
Serial.println(MRR);

String Energy = Serial.readString();
Serial.println(Energy);

String diodes = Serial.readString();
String ST = Serial.readString();
Serial.println("ON");

String PC = Serial.readString();
String S1 = Serial.readString();
String S0 = Serial.readString();

}
}
