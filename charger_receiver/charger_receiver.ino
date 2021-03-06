// Wire Slave Receiver
// Attiny45 controling a LiPo Battery and solar planel to power a PIzero


#include "TinyWireS.h"
#include "core_adc.h"


#define SHUTDOWNTIME 30000UL
#define WAITFACTOR 1000UL

unsigned long stopfor = 0;
int val = 0; // medium value
int sum = 0; // sum
int count = 0;
int sending = 0; // to store val while sending it.

uint8_t c = 0;

// PB0 is SDA
const int ledgreen = PB1; // Not a led in fact the optocoupler
// PB2 is SCL
const int ledred = PB3;
const int analogPin = ADC_Input_ADC2; // PB4;
// const int analogPin = ADC_Input_ADC0; // PB5 and RESET! = PROBLEMS!!!

bool redon = false;
bool ispion = false;
bool start_conversion = true;
// we have 3 states: auto, force on and force off.
bool automode = true;
bool forcebaton = false;
bool forceusb = false;

/* 3V according to divisor (1000+220)/220 = 5.5454 and ref = 1.1V */
/* 505/1024*1.1*5.5454 = 3.0805 V */
/* according to my testa until around 440 = 2.621 V the USB is stable */ 
#define BATCHARGED 773 /* 700 seems to make 3.8V,  773 would be 4.2 */
#define BATLOW 440 /* 2.626 too low compare to 3.0v/cell. */ 
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
      int curval = ADC_GetDataRegister();
      sum = sum + curval;
      count++;
      if (count == 10) {
        val = sum / 10;
        count = 0;
        sum = 0;
      }
      if (automode) {
        if (val<BATCHARGED) {
          digitalWrite(ledgreen, LOW);
        } else {
          digitalWrite(ledgreen, HIGH);
        }
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
    if (ispion) {
      delay(SHUTDOWNTIME); // give time to stop.
      digitalWrite(ledred, LOW); // disable 5 V USB.
      ispion = false;
    }
    delay(WAITFACTOR);
    stopfor--;
    return;
  }

  // Otherwise just switch on.
  if (!ispion) {
    digitalWrite(ledred, HIGH); // enable 5 V USB
    ispion = true;
  }

  // Forced mode for debuggging the hardware!!!
  if (!automode) {
    if (forcebaton){
      digitalWrite(ledgreen, LOW);
    } else {
      digitalWrite(ledgreen, HIGH);
    }
    if (forceusb) {
      digitalWrite(ledred, HIGH); // enable 5 V USB
    } else {
      digitalWrite(ledred, LOW); // disable 5 V USB.
    }
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
    // c = 0 : read high
    // c = 1 : read low and auto mode
    // c = 2 force bat on.
    // c = 3 force bat off.
    // c = 4 force USB on.
    // c = 5 force USB off.
    // otherwise PI sleeps for c.
    if (c == 1) {
      automode = true;
    } else if (c == 2) {
      automode = false;
      forcebaton =  true;
    } else if (c == 3) {
      automode = false;
      forcebaton = false;
    } else if (c == 4) {
      automode = false;
      forceusb = true;
    } else if (c == 5){
      automode = false;
      forceusb = false;
    }
    if (c>5) {
      automode = true;
      stopfor = c * 60;
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
