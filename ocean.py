#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import requests
import time

OCEANGPIO=23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OCEANGPIO,GPIO.OUT)
GPIO.output(OCEANGPIO,GPIO.LOW)

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
ison = False
while i < 5:
  # print("on")
  r = requests.get('https://www.apache.org')
  if (r.status_code == 200):
    r = requests.get('https://' + machinename + '/machines/' + machine_id)
    # print('https://' + machinename + '/machines/' + machine_id + '.ok')
    if (r.status_code == 200):
      GPIO.output(OCEANGPIO,GPIO.HIGH)
      print("on")
      ison = True
    time.sleep(5)
  if not ison:
    print("off")
    GPIO.output(OCEANGPIO,GPIO.LOW)
  time.sleep(5)
  i += 1

# end make sur to stop
GPIO.output(OCEANGPIO,GPIO.LOW)
