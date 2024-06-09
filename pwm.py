#!/usr/bin/python3
# apt-get install python3-pigpio
# sudo pigpiod
# before using it.

import pigpio
import RPi.GPIO as GPIO
from time import sleep
import sys

ledpin = 13				# PWM pin connected to LED
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledpin,GPIO.OUT)

pi_pwm = pigpio.pi() 
pi_pwm.set_mode(ledpin, pigpio.OUTPUT)
pi_pwm.set_PWM_frequency(ledpin, 25000)

pi_pwm.set_PWM_dutycycle(dutycycle=0, user_gpio=ledpin)

def Usage():
    print("Usage: pwm.py val (val>50 and val<100)")
    exit(1)

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    if len(sys.argv) != 2:
        Usage()
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    val = int(sys.argv[1])
    if val<50 or val>100:
        Usage()
    print(val)
    pi_pwm.set_PWM_dutycycle(dutycycle=int(val), user_gpio=ledpin)
    sleep(60.0)
