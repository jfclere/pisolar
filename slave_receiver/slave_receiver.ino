// Wire Slave Receiver
// Attiny45 controling a LiPo Rider Pro to power a PIzero


#include "TinyWireS.h"
#include "core_adc.h"


#define SHUTDOWNTIME 30000UL
#define WAITFACTOR 60000UL

unsigned long stopfor = 0;
int val = 0;
int sending = 0; // to store val while sending it.

uint8_t c = 0;
const int ledgreen = PB1;
const int ledred = PB3;
const int analogPin = ADC_Input_ADC2; // PB4;
bool redon = false;
bool ispion = false;
bool start_conversion = true;

/* 3V according to divisor (1000+220)/220 = 5.5454 and ref = 1.1V */
/* 505/1024*1.1*5.5454 = 3.0805 V */
/* according to my testa until around 440 = 2.621 V the USB is stable */ 
#define BATLOW 505
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
      if (val<BATLOW) {
        digitalWrite(ledgreen, HIGH);
        ispion = false;
      } else {
        digitalWrite(ledgreen, LOW);
        ispion = true;
      }
      ADC_StartConversion();
    }
  }

  /* do nothing until we don't know if we have enough battery */
  if (!val)
     return;

  /* Not enough battery and off do nothing */
  if (val<BATLOW && !ispion)
     return;

  
  // stop and sleep.
  if (stopfor) {
    // We have just received a stop for the PI
    delay(SHUTDOWNTIME); // give time to stop.
    digitalWrite(ledgreen, HIGH);
    ispion = false;
    if (redon) {
      digitalWrite(ledred, LOW);
      redon = false;
    } else {
      digitalWrite(ledred, HIGH);
      redon = true;
    }
    delay(stopfor * WAITFACTOR);
    stopfor = 0;
    val = 0;
    return;
  }

  // Otherwise just switch on.
  if (!ispion) {
    digitalWrite(ledgreen, LOW);
    ispion = true;
  }
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
    // c = 0 : read high, c = 1 : read low, otherwise PI sleeps for c.
    if (c>1) {
      stopfor = c;
    }
  }
}
void requestEvent ()
{
  // Send the low or high value
  if (c) {
    TinyWireS.send((uint8_t) (sending%256));
  } else {
    sending = val;
    TinyWireS.send((uint8_t) (sending/256));
  }
}
