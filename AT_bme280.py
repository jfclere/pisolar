#!/usr/bin/python3

import sys
import AT_http_s
from AT_nodeinfo import nodeinfo
from bme280 import bme280
from writereg import writereg

def readandsend(info):
    sensor = bme280()
    try:
        temperature, pressure, humidity = sensor.readBME280All()
    except Exception as e:
        print("BME280 read error: " + str(e))
        return True

    mess = "Tmp : " + str(round(temperature, 2)) + "\n"
    mess = mess + "Prs : " + str(round(pressure, 2)) + "\n"
    mess = mess + "Hum : " + str(round(humidity, 2)) + "\n"
    print(mess)

    url = 'https://' + info.server + '/webdav/' + info.REMOTE_DIR + '/temp.txt'
    if AT_http_s.HTTPPUT(url, mess, info.login, info.password):
        print("PUT failed")
        return True
    print("PUT done")
    return False

if __name__ == '__main__':
    AT_http_s.AT().AT_port()

    info = nodeinfo()
    print('server: ' + info.server)
    print('machine_id: ' + info.machine_id)
    if info.read():
        print("nodeinfo.read() Failed, using defaults")

    if readandsend(info):
        sys.exit(1)

    mywritereg = writereg(3)
    mywritereg.write(8, info.WAIT_TIME)
    os.system("sudo init 0")
    sys.exit(0)

