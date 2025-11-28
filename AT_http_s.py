import time
from datetime import datetime

import serial
import sys


class AT:
    def __init__(self, port='/dev/ttyS0', Baud_rate=115200):
        self.port = port
        self.rate = Baud_rate

    def AT_port(self):
        print("Send AT verification port connection")
        try:
            global ser
            ser = serial.Serial(self.port, self.rate, timeout=1)
            print("Send AT")
            ser.write(b'AT\r\n')
            res_at = ser.readlines()[1].decode('utf-8').strip()
            print(res_at)
            if res_at == "OK":
                print('Serial port connection successful')
                return True
        except serial.SerialException as e:
            sys.exit(e)


def HTTPINIT():
    ser.write(b'AT+HTTPINIT\r\n')
    res_httpinit = ser.readlines()[1].decode('utf-8').strip()
    print(res_httpinit)
    if res_httpinit == "ERROR":
        print('HTTP Initialization failed') 
        return False
    else:
        print('HTTP Initialization Done')
        return True


class HTTPPARA:
    def __init__(self, url='https://www.waveshare.cloud/api/sample-test/'):
        self.url = url

    def PARA(self):
        print("Connecting to URL")
        command = 'AT+HTTPPARA=URL,{}\r\n'.format(self.url)
        ser.write(command.encode())
        res_PARA = ser.readlines()[1].decode('utf-8').strip()
        print(res_PARA)
        if res_PARA == "OK":
            print("Connected to:" + self.url)
            return False
        else:
            print("Connection failed")
            return True


def HTTPDATA(data):
    l = str(len(data))
    command = 'AT+HTTPDATA={},1000\r\n'.format(l)
    ser.write(command.encode())
    # ser.write(string.encode())
    res_httpdata = ser.readlines()[1].decode('utf-8').strip()
    print(res_httpdata)
    if res_httpdata == 'DOWNLOAD':
        try:
            ser.write(data.encode())
            res_inputdata = ser.readlines()[1].decode('utf-8').strip()
            print(res_inputdata)
        except serial.SerialException as e:
            sys.exit(e)

    # while res_httpdata == "ERROR":
    #     ser.write(b'AT+HTTPDATA=2,1000\n\r')
    # ser.write(string.encode())
    # time.sleep(2)
    # print(data.encode())
    # ser.write(data.encode())


def HTTPACTION(action):
    global response_length
    print('send request')
    command = 'AT+HTTPACTION={}\r\n'.format(action)
    ser.write(command.encode())
    res_aciton = ser.readlines()[1].decode('utf-8').strip()
    # if res_aciton == 'OK':
    #     print('Waiting for response!')
    #     while True:
    #         print('.', end='')
    #         line = ser.readline().decode('utf-8').strip()
    #         if line.startswith("+HTTPACTION: "):
    #             res_callback = line.split(": ")[1]  # Extract the part after ": "
    #             action, status_code, response_length = res_callback.split(",")[:3]
    #
    #             if int(action) == 1:
    #                 request_type = "POST"
    #             else:
    #                 request_type = "GET"
    #             print('')
    #             print("Request Type:", request_type)
    #             print("Status Code:", status_code)
    #             print("Response Length:", response_length)
    #             break
    if res_aciton == 'OK':
        print('Waiting for response!')
        while True:
            print('.', end='')
            line = ser.readline().decode('utf-8').strip()

            if not line.startswith("+HTTPACTION: "):
                continue

            res_callback = line.split(": ")[1]  # Extract the part after ": "
            action, status_code, response_length = res_callback.split(",")[:3]

            request_type = "POST" if int(action) == 1 else "GET"

            print('\n Method: ', request_type)
            print('Status:', status_code)
            print('Content-Length:', response_length)
            status_code = int(status_code)
            if status_code >= 200 and status_code < 300:
                print('OK!')
                HTTPREAD(response_length)
            else:
                print('Not OK: ', status_code)
            break


def HTTPREAD(data_length):
    print('Reading Response')
    command = 'AT+HTTPREAD=0,{}\r\n'.format(data_length)
    ser.write(command.encode())
    res_aciton = ser.readlines()[4].decode('utf-8').strip()
    print(res_aciton)
    print("End Response")
    # HTTPTERM()


def HTTPTERM():
    print("Closing HTTP connection")
    command = 'AT+HTTPTERM\r\n'
    ser.write(command.encode())
    res_term = ser.readlines()[1].decode('utf-8').strip()
    if res_term == 'OK':
        print("bye")

def HTTPDATE():
    print("Reading date")
    command = 'AT+CCLK?\r\n'
    ser.write(command.encode())
    res = ser.readlines()[1].decode('utf-8').strip()
    if "+CCLK:" not in res:
        return None
    idx1 = res.find("\"")
    idx2 = res.find("+", idx1)
    sdate = res[idx1+1:idx2] 
    try:
        datetime_object = datetime.strptime(sdate, '%Y/%m/%d,%H:%M:%S') 
        print(datetime_object)
    except:
        return None
    return datetime_object

if __name__ == '__main__':
    # ser = serial.Serial('COM6', 115200, timeout=1)
    AT().AT_port()
    if HTTPINIT():
        print("HTTPINIT failed")
        sys.exit(e)
    mydate = HTTPDATE()
    if not mydate:
        print("HTTPDATE failed")
        sys.exit(0)
    HTTPPARA().PARA()
    # HTTPPARA('http://116.182.15.2:8000').PARA()
    print('Continue？yes/no')
    user_input = input()
    if user_input.lower() == 'y' or user_input.lower() == 'yes':
        print("Enter your data to send")
        data = input()
        HTTPDATA(data)
        HTTPACTION(1)
        while True:
            print("Request end")
            print("Continue？yes/no")
            user_input = input()
            if user_input.lower() == 'y' or user_input.lower() == 'yes':
                print("Enter data to send")
                data = input()
                HTTPDATA(data)
                HTTPACTION(1)
            else:
                HTTPACTION(0)
                HTTPTERM()
                break
    elif user_input.lower() == 'no':
        HTTPACTION(0)
        HTTPTERM()
    else:
        print("Done！")

