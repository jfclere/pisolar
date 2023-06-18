#!/usr/bin/python

import time
import math
import sys
import os
import requests
import socket

from nodeinfo import nodeinfo
from readreg import readreg

#
# This report information to the server
#

class reportserver:

  # report our information to the server
  def report(self, nodeinfo, readreg):
    val = readreg.read(0)
    r = requests.get('https://' + self.server + '/machines/report-' + self.machine_id + '-' + val)
    if (r.status_code != 404):
      return False
    val = readreg.read(6)
    r = requests.get('https://' + self.server + '/machines/reportold-' + self.machine_id + '-' + val)
    if (r.status_code != 404):
      return False
    # report ip
    hostname = socket.gethostname()
    val = socket.gethostbyname(hostname)
    r = requests.get('https://' + self.server + '/machines/reportip-' + self.machine_id + '-' + val)
    if (r.status_code != 404):
      return False
    return True 

if __name__=='__main__':

  info = nodeinfo()
  print('server: ' + info.server)
  print('machine_id: ' + info.machine_id)
  if info.read():
    print("Failed no info!")
    exit()
  else:
    print(info.REMOTE_DIR)
    print(info.WAIT_TIME)
    print(info.BAT_LOW)
    print(info.GIT_VER)
    print(info.BATCHARGED)
    print(info.TIME_ACTIVE)

  reg = readreg()

  report = reportserver()
  if report.report(info, reg):
    print("Failed can't report")
  print("Done")
