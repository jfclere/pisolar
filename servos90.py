#!/usr/bin/python3
# from https://ben.akrin.com/?p=9158
# sudo apt-get install python3-rpi.gpio
# sudo apt-get install python3-pigpio
# requires:  sudo pigpiod
# note the servos are powered directly from the lipo battery.
import RPi.GPIO as GPIO
import pigpio
import time
 
servoh = 14
servov = 4
 
# more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
 
pwm = pigpio.pi() 
pwm.set_mode(servoh, pigpio.OUTPUT)
pwm.set_mode(servov, pigpio.OUTPUT)
 
pwm.set_PWM_frequency( servoh, 50 )
pwm.set_PWM_frequency( servov, 50 )
 
print( "90 deg" )
pwm.set_servo_pulsewidth( servoh, 1500 ) ;
pwm.set_servo_pulsewidth( servov, 1500 ) ;
time.sleep( 10 )
 
# turning off servo
pwm.set_PWM_dutycycle(servoh, 0)
pwm.set_PWM_frequency( servoh, 0 )

pwm.set_PWM_dutycycle(servov, 0)
pwm.set_PWM_frequency( servov, 0 )
