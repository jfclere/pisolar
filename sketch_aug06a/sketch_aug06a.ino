#include "core_adc.h"

#define MAXUPTIME 60000UL // 10 minutes

// PB0 is SDA
const int readpicow = PB1;
// PB2 is SCL
const int resetpicow = PB3;
const int analogPin = ADC_Input_ADC2; // PB4;

bool ispion = true; // picow is running
int picooldval = LOW; // picow will toggle the value regularly
unsigned long uptime = 0; // last time the picow reported running

unsigned short   *batcharged;
unsigned short   *val; // medium value
volatile uint8_t i2c_regs[17]; // Like my other projects if we want to use I2C one day

#define BATCHARGED 400 // should be 600 for the 12V version???

int sum = 0; // sum
int count = 0;

bool start_conversion = true;
void setup() {
  val = (unsigned short *) &i2c_regs[0];
  batcharged = (unsigned short *) &i2c_regs[4];
  *batcharged = BATCHARGED;
  pinMode(readpicow, INPUT);
  pinMode(resetpicow, OUTPUT);
  digitalWrite(resetpicow, HIGH); // leave it running
}

void loop() {
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
    }
    ADC_StartConversion();
  }
  
  /* do nothing until we don't have a value */
  if (!*val)
     return;
     
  if (*val<*batcharged) {
    digitalWrite(resetpicow, HIGH);
  } else {
    // check if we need to reset the picow as it doesn't control the battery correctly
    int picoval;
    picoval = digitalRead(readpicow);
    if (picoval != picooldval) {
      uptime = millis();
      // Testing ... picooldval = picoval;
    } else {
      // The value is unchanged
      unsigned long currentMillis = millis();
      unsigned long waited;
      if (uptime > currentMillis) {
        // we wrapped around 0. millis() wrap around to 0 after about 49 days
        waited = 4294967295UL - uptime;
        waited = waited + currentMillis;
      } else {
        waited = currentMillis - uptime;
      }
      if (waited > MAXUPTIME) {
        // Reset the picow.
        digitalWrite(resetpicow, LOW);
        uptime = currentMillis;
        digitalWrite(resetpicow, HIGH);
      }
    }
  }
}
