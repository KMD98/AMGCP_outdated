// Example modded by Dan to control both motors on one drive to go forward then backwards. Default baud is 9600

#include <SoftwareSerial.h>
#include <Sabertooth.h>

SoftwareSerial SWSerial(NOT_A_PIN, 18); // RX on no pin (unused), TX on pin 11 (to S1).
Sabertooth ST(128, SWSerial); // Address 128, and use SWSerial as the serial port.

void setup()
{
  SWSerial.begin(9600);
  ST.autobaud();
}

void loop()
{
  int power;
  
  // Ramp from -127 to 127 (full reverse to full forward), waiting 20 ms (1/50th of a second) per value.
  for (power = -127; power <= 127; power ++)
  {
    ST.motor(1, power);
    ST.motor(2,power);
    delay(20);
  }
  
  // Now go back the way we came.
  for (power = 127; power >= -127; power --)
  {
    ST.motor(1, power);
    ST.motor(2,power);
    delay(20);
  }
}
