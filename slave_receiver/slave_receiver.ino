// Wire Slave Receiver


#include "TinyWireS.h"

#define SHUTDOWNTIME 1000
#define WAITFACTOR 60000

bool up = true; // start it!!!
int stopfor = 0;
int val = 0;
// int analogPin = ADC2;
uint8_t c = 0;
const int ledgreen = PB1;
const int ledred = PB3;
bool redon = false;
bool greenon = false;

void setup()
{
  TinyWireS.begin(0x04);                // join i2c bus with address #4
  TinyWireS.onReceive(receiveEvent); // register event
  TinyWireS.onRequest(requestEvent); // interrupt handler for when data is wanted
  pinMode(ledgreen, OUTPUT);
  pinMode(ledred, OUTPUT);
}

void loop()
{
  TinyWireS_stop_check();
  /* 
  
  delay(100);
  val = analogRead(analogPin);
  if (stopfor) {
    // We have just received a stop for the PI
    delay(SHUTDOWNTIME); // give time to stop.
  }
  if (up)
    digitalWrite(led, HIGH);
  else {
    // stop and wait for stopfor seconds 
    digitalWrite(led, LOW);
    if (stopfor) {
      delay(stopfor * WAITFACTOR);
      stopfor = 0;
      up = true;
    }
  }
  */
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(uint8_t howMany)
{
  if (howMany < 1)
    return;
  while(howMany--)
  {
    c = TinyWireS.receive(); // receive byte as a character
    if (redon)
      digitalWrite(ledred, LOW);
    else
      digitalWrite(ledred, HIGH);
    /* if (c) {
      stopfor = c;
      up = false;
    }
    */
  }
}
void requestEvent ()
{
  TinyWireS.send(c);
  if (greenon)
      digitalWrite(ledgreen, LOW);
    else
      digitalWrite(ledgreen, HIGH);

  /*
  if (c)
    TinyWireS.send(val/256);
  else
    TinyWireS.send(val%256);
  */
}
