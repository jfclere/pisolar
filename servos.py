#!/usr/bin/python3
# from https://ben.akrin.com/?p=9158
# sudo apt-get install python3-rpi.gpio
# sudo apt-get install python3-pigpio
# requires:  sudo pigpiod
# note the servos are powered directly from the lipo battery.
import RPi.GPIO as GPIO
import pigpio
import time
 
servo = 14
#servo = 4
 
# more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
 
pwm = pigpio.pi() 
pwm.set_mode(servo, pigpio.OUTPUT)
 
pwm.set_PWM_frequency( servo, 50 )
 
print( "0 deg" )
pwm.set_servo_pulsewidth( servo, 500 ) ;
time.sleep( 10 )
 
print( "90 deg" )
pwm.set_servo_pulsewidth( servo, 1500 ) ;
time.sleep( 10 )
 
print( "180 deg" )
pwm.set_servo_pulsewidth( servo, 2500 ) ;
time.sleep( 10 )
 
# turning off servo
pwm.set_PWM_dutycycle(servo, 0)
pwm.set_PWM_frequency( servo, 0 )
