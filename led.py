#!/usr/bin/python3
# blue : activity via dtoverlay=act-led,gpio=26
# green : network is running
# red : the RPI is taking pictures...

import RPi.GPIO as GPIO
import os
import requests
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
f = open("/etc/machine-id", "r")
machine_id = f.read().rstrip()
# print("*" + machine_id + "*")
filename = os.getenv("HOME")+"/.netrc"
f = open(filename, "r")
txt = f.readline()
x = txt.split(" ")
machinename = x[1].rstrip()
# print("*" + machinename + "*")
# loop 10 times testing network and server
# somehow for about 2 minutes. 
i = 0
while i < 11:
  # print("on")
  r = requests.get('https://www.apache.org')
  if (r.status_code == 200):
    GPIO.output(13,GPIO.HIGH)
  r = requests.get('https://' + machinename + '/machines/' + machine_id)
  # print('https://' + machinename + '/machines/' + machine_id + '.ok')
  if (r.status_code == 200):
    GPIO.output(19,GPIO.HIGH)
  time.sleep(5)
  # print("off")
  GPIO.output(13,GPIO.LOW)
  GPIO.output(19,GPIO.LOW)
  time.sleep(5)
  i += 1
