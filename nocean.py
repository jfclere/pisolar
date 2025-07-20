#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import time
import socket
from nodeinfo import nodeinfo

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

while True:
  if myinfo.TIME_ACTIVE > 0:
    GPIO.output(OCEANGPIO,GPIO.HIGH)
    print("on for " + str(myinfo.TIME_ACTIVE) + " Minutes")
    time.sleep(60*myinfo.TIME_ACTIVE)
  else:
    GPIO.output(OCEANGPIO,GPIO.LOW)
    print("off for 1 Minutes")
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
