#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

servoPIN = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 14 for PWM with 50Hz
p.start(0) # Initialization
i = 0
try:
  while True:
    p.ChangeDutyCycle(i)
    i = i + 1
    time.sleep(5)
    if i == 100:
       break
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
