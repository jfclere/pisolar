#!/usr/bin/python3
# test charging using gpio=26

import RPi.GPIO as GPIO

CHARGEGPIO=26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CHARGEGPIO,GPIO.IN)

i = GPIO.input(CHARGEGPIO)

print(i)

