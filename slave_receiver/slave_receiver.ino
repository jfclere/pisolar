// Wire Slave Receiver


#include "TinyWireS.h"
#include "core_adc.h"


#define SHUTDOWNTIME 1000
#define WAITFACTOR 60000

bool up = true; // start it!!!
int stopfor = 0;
int val = 0;

uint8_t c = 0;
const int ledgreen = PB1;
const int ledred = PB3;
const int analogPin = ADC_Input_ADC2; // PB4;
bool redon = false;
bool greenon = false;
bool start_conversion = true;

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
  if (start_conversion) {
    start_conversion = false;
    ADC_SetVoltageReference(ADC_Reference_Internal_1p1);
    ADC_SetInputChannel(analogPin);
    ADC_StartConversion();
  } else {
    /* ADC conversion in progress */
    if(!ADC_ConversionInProgress()) {
      /* we have a value, read it */
      val = ADC_GetDataRegister();
      // start_conversion = true;
      if (greenon) {
       digitalWrite(ledgreen, LOW);
        greenon = false;
      } else {
        digitalWrite(ledgreen, HIGH);
        greenon = true;
      }
      ADC_StartConversion();
    }
  }
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
    if (redon) {
      digitalWrite(ledred, LOW);
      redon = false;
    } else {
      digitalWrite(ledred, HIGH);
      redon = true;
    }
    /* if (c) {
      stopfor = c;
      up = false;
    }
    */
  }
}
void requestEvent ()
{
  // TinyWireS.send(c);
  if (c)
    TinyWireS.send((uint8_t) (val%256));
  else
    TinyWireS.send((uint8_t) (val/256));
 /*     
  if (greenon) {
      digitalWrite(ledgreen, LOW);
      greenon = false;
  } else {
      digitalWrite(ledgreen, HIGH);
      greenon = true;
  }
  */

  /*
  if (c)
    TinyWireS.send(val/256);
  else
    TinyWireS.send(val%256);
  */
}
