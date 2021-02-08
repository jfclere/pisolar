// Wire Slave Receiver


#include <Wire.h>

#define SHUTDOWNTIME 1000
#define WAITFACTOR 60000

bool up = true; // start it!!!
int stopfor = 0;
int count = 0;

void setup()
{
  Wire.begin(4);                // join i2c bus with address #4
  Wire.onReceive(receiveEvent); // register event
  Wire.onRequest(requestEvent); // interrupt handler for when data is wanted
  pinMode(11, OUTPUT); // Relay to PI on 11
}

void loop()
{
  delay(100);
  if (stopfor) {
    // We have just received a stop for the PI
    delay(SHUTDOWNTIME); // give time to stop.
  }
  if (up)
    digitalWrite(11, HIGH);
  else {
    // stop and wait for stopfor seconds 
    digitalWrite(11, LOW);
    if (stopfor) {
      delay(stopfor * WAITFACTOR);
      stopfor = 0;
      up = true;
    }
  }
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany)
{
  while(Wire.available())
  {
    char c = Wire.read(); // receive byte as a character
    if (c) {
      stopfor = c;
      up = false;
    }
    count++;
  }
}
void requestEvent ()
{
  Wire.write(count);
}
