#!/usr/bin/python3
import RPi.GPIO as GPIO

PIN=26
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN,GPIO.OUT)
GPIO.output(PIN,GPIO.LOW)
