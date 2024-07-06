// Wire Slave Receiver
// Attiny45 controling a LiPo Battery and solar planel to power a PIzero


#include "TinyWireS.h"
#include "core_adc.h"


#define SHUTDOWNTIME 30000UL
#define WAITFACTOR 1000UL
#define MAXUPTIME 21600000UL
#define KEEPOFFTIME 10ULL

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
#define AUTO  0x01
#define BATON 0x02
#define USBON 0x04

/* 3V according to divisor (1000+220)/220 = 5.5454 and ref = 1.1V */
/* 505/1024*1.1*5.5454 = 3.0805 V */
/* according to my testa until around 440 = 2.621 V the USB is stable */ 
#define BATCHARGED 800 /* 700 seems to make 3.8V,  773 would be 4.2 */
#define BATLOW 600 /* 440 : 2.626 too low compare to 3.0v/cell. 600: 3.93 V 504 ~ 3 V*/ 

volatile byte reg_position;
volatile uint8_t i2c_regs[17];
/* We store there: val (current value), batlow, batchar, valstart, stopfor (8bytes) and testmode (1 byte) */
unsigned short 	*batlow;
unsigned short 	*batcharged;
unsigned short 	*val; // medium value
unsigned short  *valstart; // value when the PI has been switched on
unsigned long long *stopfor;

unsigned long uptime = 0;   // time when the RPI started
unsigned long waittime = 0; // time when the wait for wait for shutdown started

#define TESTMODEOFFSET 16


void setup()
{
  TinyWireS.begin(0x04);                // join i2c bus with address #4
  TinyWireS.onReceive(receiveEvent); // register event
  TinyWireS.onRequest(requestEvent); // interrupt handler for when data is wanted
  pinMode(ledgreen, OUTPUT);
  pinMode(ledred, OUTPUT);
  digitalWrite(ledred, LOW); // disable 5 V USB.
  digitalWrite(ledgreen, LOW); // charge battery
  val = (unsigned short *) &i2c_regs[0];
  batlow = (unsigned short *) &i2c_regs[2];
  batcharged = (unsigned short *) &i2c_regs[4];
  valstart = (unsigned short *) &i2c_regs[6];
  stopfor = (unsigned long long *) &i2c_regs[8];
  i2c_regs[TESTMODEOFFSET] = AUTO;
  *batlow = BATLOW;
  *batcharged = BATCHARGED;
  *stopfor = 0ULL;  
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
        *val = sum / 10;
        count = 0;
        sum = 0;
      }

      volatile bool automode =  i2c_regs[TESTMODEOFFSET]&AUTO;
      if (automode) {
        if (*val<*batcharged) {
          digitalWrite(ledgreen, LOW);
        } else {
          digitalWrite(ledgreen, HIGH);
        }
      }
      ADC_StartConversion();
    }
  }

  /* do nothing until we don't know if we have enough battery */
  if (!*val)
     return;

  /* Not enough battery and off do nothing */
  if (*val< *batlow && !ispion)
     return;
  
  // stop and sleep.
  if (*stopfor != 0ULL) {
    // We have received a stop for the PI
    unsigned long currentMillis = millis();
    // millis() wrap around to 0 after about 49 days
    unsigned long waited;
    if (waittime>currentMillis) {
      // we wrapped around 0.
      waited = 4294967295UL - waittime;
      waited = waited + currentMillis;
    } else {
      waited = currentMillis - waittime;
    } 
    if (ispion) {
      if (waittime) {
        // give time to stop.
        if (waited > SHUTDOWNTIME) {
          digitalWrite(ledred, LOW); // disable 5 V USB.
          ispion = false;
          waittime = currentMillis;
        } 
      } else {
        waittime = currentMillis;
      }
    } else {
      /* wait for WAITFACTOR * stopfor */
      if (waited > WAITFACTOR) {
        waittime = currentMillis;
        *stopfor = *stopfor -1;
      }
    }
    return;
  }

  // Forced mode for debuggging the hardware!!!
  volatile bool automode =  i2c_regs[TESTMODEOFFSET]&AUTO;
  volatile bool forcebaton = i2c_regs[TESTMODEOFFSET]&BATON;
  volatile bool forceusb = i2c_regs[TESTMODEOFFSET]&USBON;
  if (!automode) {
    if (forcebaton) {
      digitalWrite(ledgreen, LOW);
    } else {
      digitalWrite(ledgreen, HIGH);
    }
    if (forceusb) {
      digitalWrite(ledred, HIGH); // enable 5 V USB
      ispion = true;
    } else {
      digitalWrite(ledred, LOW); // disable 5 V USB.
      ispion = false;
    }
  } else {
    // Otherwise just switch on.
    if (!ispion) {
      uptime = millis();
      *valstart = *val;
      digitalWrite(ledred, HIGH); // enable 5 V USB
      ispion = true;
    } else {
      /* The PI is on, make sure it doesn't drain for ever */
      if (uptime) {
        unsigned long currentMillis = millis();
        // millis() wrap around to 0 after about 49 days
        unsigned long waited;
        if (uptime>currentMillis) {
          // we wrapped around 0.
          waited = 4294967295UL - uptime;
          waited = waited + currentMillis;
        } else {
          waited = currentMillis - uptime;
        }     
        if (waited > MAXUPTIME) {
          /* After 6 hours */
          *stopfor = KEEPOFFTIME; /* stop for SHUTDOWNTIME + 10*WAITFACTOR */
          uptime = 0;
        }
      }
    }
  }
  return;
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(uint8_t howMany)
{
  if (howMany < 1)
    return;
  reg_position = TinyWireS.receive();
  howMany--;
  if (!howMany) {
    // This write was only to set the buffer for next read
    return;
  }

  while(howMany--) {
    // i2c_regs[reg_position] =  (uint8_t volatile) TinyWireS.receive();
    i2c_regs[reg_position] = TinyWireS.receive();
    reg_position++;
    if (reg_position >= sizeof(i2c_regs)-1) {
      reg_position = 0;
    }
  }
}
    // c = 0 : read high
    // c = 1 : read low and auto mode
    // c = 2 force bat on.
    // c = 3 force bat off.
    // c = 4 force USB on.
    // c = 5 force USB off.
    // otherwise PI sleeps for c.
    /* need to process the register somehow
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
    */
    
void requestEvent ()
{
  // Send the registers
  TinyWireS.send(i2c_regs[reg_position]);
  // Increment the reg position on each read, and loop back to zero
  reg_position++;
  if (reg_position >= sizeof(i2c_regs)) {
        reg_position = 0;
    }
}
