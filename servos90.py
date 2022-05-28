#!/usr/bin/python3
# from https://ben.akrin.com/?p=9158
# sudo apt-get install python3-rpi.gpio
# sudo apt-get install python3-pigpio
# requires:  sudo pigpiod
# note the servos are powered directly from the lipo battery.
import RPi.GPIO as GPIO
import pigpio
import time
import sys
 
servoh = 14
servov = 4

hor = 1500
ver = 1500
 
# more info at http://abyz.me.uk/rpi/pigpio/python.html#set_servo_pulsewidth
# range is 500-2500
# 1500 : 90 deg

if len(sys.argv) == 3:
   hor = int(sys.argv[1])
   ver = int(sys.argv[2])
if len(sys.argv) == 2:
   # read the file
   text_file = open("/home/pi/pisolar/servos90.txt")
   hor = int(text_file.readline())
   ver = int(text_file.readline())
   text_file.close()
   print('hor: ' + str(hor) + ' ver: ' + str(ver))
   if sys.argv[1] == "Left":
       hor = hor + 50
       if hor > 2500:
          hor = 2500 
   elif sys.argv[1] == "Right":
       hor = hor - 50
       if hor < 500:
          hor = 500 
   elif sys.argv[1] == "Down":
       ver = ver + 50
       if ver > 2500:
          ver = 2500 
   elif sys.argv[1] == "Up":
       ver = ver - 50
       if ver < 500:
          ver = 500 
   else:
       print('hor: ' + str(hor) + ' ver: ' + str(ver))

if hor > 2500 or hor < 500:
   hor = 1500
 
if ver > 2500 or ver < 500:
   ver = 1500

pwm = pigpio.pi() 
pwm.set_mode(servoh, pigpio.OUTPUT)
pwm.set_mode(servov, pigpio.OUTPUT)
 
pwm.set_PWM_frequency( servoh, 50 )
pwm.set_PWM_frequency( servov, 50 )
 
pwm.set_servo_pulsewidth( servoh, hor ) ;
pwm.set_servo_pulsewidth( servov, ver ) ;
time.sleep( 0.5 )
 
# turning off servo
pwm.set_PWM_dutycycle(servoh, 0)
pwm.set_PWM_frequency( servoh, 0 )

pwm.set_PWM_dutycycle(servov, 0)
pwm.set_PWM_frequency( servov, 0 )

# save the value in a file
text_file = open("/home/pi/pisolar/servos90.txt", "w")
text_file.write(str(hor) + "\n")
text_file.write(str(ver) + "\n")
text_file.close()
