#!/usr/bin/python3
# from https://www.freva.com/hc-sr501-pir-motion-sensor-on-raspberry-pi/
#
# in the service
#[Service]
#Restart=always 
#
# and:
#[Unit]
#Description=Image sender service
#After=network.target
#StartLimitIntervalSec=60
#StartLimitBurst=5
#FailureAction=reboot
#

import RPi.GPIO as GPIO
import time
import os
import requests
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 23
GPIO.setup(PIR_PIN, GPIO.IN)

print('Starting up the PIR Module (Control C to stop)')
time.sleep(1)

f = open("/etc/machine-id", "r")
machine_id = f.read().rstrip()
print("*" + machine_id + "*")
filename = os.getenv("HOME")+"/.netrc"
f = open(filename, "r")
txt = f.readline()
x = txt.split(" ")
machinename = x[1].rstrip()
print("*" + machinename + "*")

print ('Ready')

while True:
  if GPIO.input(PIR_PIN):
    print('Motion Detected')
    r = requests.get('https://' + machinename + '/machines/' + machine_id)
    if (r.status_code == 200): 
      print('Motion Reported')
  time.sleep(1)
