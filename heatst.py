#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import time
import socket
from nodeinfo import nodeinfo
import bme280

OCEANGPIO=26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OCEANGPIO,GPIO.OUT)
GPIO.output(OCEANGPIO,GPIO.LOW)

# wait until we have an IP
i = 1
while i < 30:
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
  except: 
    time.sleep(1)
    i += 1
    continue
  break
net = True 
if i == 30:
  # We don't have network
  net = False

if not net:
  print("NO Network!")
  exit(1)

etag = ""
myinfo = nodeinfo()
bme280 = bme280.bme280()
if myinfo.readsaved():
  # Nothing saved
  print("NO Save values!")
else:
  etag = myinfo.ETAG

if myinfo.read():
  # Use some default values
  print("myinfo.read() Failed!");
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False
else:
  myinfo.saveconf()

# We want the thermostat so use myinfo.TIME_ACTIVE as temperature
while True:
  if myinfo.TIME_ACTIVE > 0:
    temperature,pressure,humidity = bme280.readBME280All()
    if myinfo.TIME_ACTIVE > temperature:
      GPIO.output(OCEANGPIO,GPIO.HIGH)
      print("on until " + str(myinfo.TIME_ACTIVE) + " C have now " + str(temperature))
    else:
      print("off for 1 Minutes")
      GPIO.output(OCEANGPIO,GPIO.LOW)
  else:
    GPIO.output(OCEANGPIO,GPIO.LOW)
    print("off for 1 Minutes")
  print("wait for 1 Minutes")
  time.sleep(60)
  if not myinfo.read():
    # check the etag for change and save configuration
    if etag != myinfo.ETAG:
      print("ETAG: " + etag + " New: " + myinfo.ETAG)
      etag = myinfo.ETAG
      myinfo.saveconf()

  print("Done")

# end make sure to stop
GPIO.output(OCEANGPIO,GPIO.LOW)
