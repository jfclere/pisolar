#!/usr/bin/python3

# Python ssl (OpenSSL) does the TLS crypto.
# SIM7028 transparent mode (AT+CIPMODE=1): serial becomes a raw TCP byte pipe.
#
# Architecture:
#   ssl.wrap_socket(app_sock) <-> socketpair <-> bridge thread <-> serial (transparent) <-> remote server

import time
import serial
import sys
import socket
import ssl
import threading

ser = None
running = True

def sendcmd(cmd, timeout=2):
    print(">>> " + cmd)
    ser.write((cmd + '\r\n').encode())
    time.sleep(0.5)
    lines = []
    end = time.time() + timeout
    while time.time() < end:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                print("<<< " + line)
            lines.append(line)
            if line == 'OK' or line == 'ERROR' or line == 'CONNECT':
                break
        else:
            time.sleep(0.05)
    return lines

def sim_open(host, port):
    # Check network registration
    sendcmd('AT+CEREG?')
    sendcmd('AT+CGATT?')
    sendcmd('AT+CGDCONT?')
    sendcmd('AT+CGACT?')

    # Clean up any previous sessions
    sendcmd('AT+HTTPTERM')
    sendcmd('AT+CACLOSE=0')
    sendcmd('AT+CIPCLOSE=0')
    sendcmd('AT+CIPSHUT')
    time.sleep(1)

    # Try 1: CIPSTART with old IP stack init
    sendcmd('AT+CSTT="tm"')
    sendcmd('AT+CIICR', timeout=10)
    sendcmd('AT+CIFSR')
    sendcmd('AT+CIPMODE=1')
    res = sendcmd('AT+CIPSTART="TCP","{}",{}'.format(host, port), timeout=30)
    for line in res:
        if 'CONNECT' in line:
            print("Transparent mode active to {}:{}".format(host, port))
            return True

    # Try 2: CAOPEN raw TCP (buffered mode)
    print("CIPSTART failed, trying CAOPEN...")
    sendcmd('AT+CIPMODE=0')
    res = sendcmd('AT+CAOPEN=0,0,0,"{}",{}'.format(host, port), timeout=30)
    for line in res:
        if '+CAOPEN: 0,0' in line:
            print("CAOPEN connected to {}:{} (buffered mode)".format(host, port))
            return True

    print("TCP connection failed")
    return False

def sim_close():
    global running
    running = False
    # Exit transparent mode: 1s pause, +++, 1s pause
    time.sleep(1)
    ser.write(b'+++')
    time.sleep(1)
    sendcmd('AT+CIPCLOSE=0')
    sendcmd('AT+CIPMODE=0')
    sendcmd('AT+CNACT=0,0')

# Bridge: transport_sock <-> serial (transparent mode, raw bytes)
def bridge(transport_sock):
    global running

    def serial_to_sock():
        while running:
            try:
                n = ser.in_waiting
                if n > 0:
                    data = ser.read(n)
                    transport_sock.sendall(data)
                else:
                    time.sleep(0.005)
            except Exception as e:
                print("serial_to_sock error: " + str(e))
                return

    def sock_to_serial():
        while running:
            try:
                data = transport_sock.recv(1024)
                if not data:
                    return
                ser.write(data)
            except Exception as e:
                print("sock_to_serial error: " + str(e))
                return

    t1 = threading.Thread(target=serial_to_sock, daemon=True)
    t2 = threading.Thread(target=sock_to_serial, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

def connect_ssl(host, port):
    if not sim_open(host, port):
        return None

    app_sock, transport_sock = socket.socketpair()

    t = threading.Thread(target=bridge, args=(transport_sock,), daemon=True)
    t.start()

    ctx = ssl.create_default_context()
    ssl_sock = ctx.wrap_socket(app_sock, server_hostname=host)
    print("TLS handshake complete: " + ssl_sock.version())
    return ssl_sock

if __name__ == '__main__':
    host = "jfclere.myddns.me"
    port = 443
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    sendcmd('AT')

    ssl_sock = connect_ssl(host, port)
    if not ssl_sock:
        print("Connection failed")
        sys.exit(1)

    # Example: GET the machine config
    from AT_nodeinfo import nodeinfo
    info = nodeinfo()
    request = "GET /machines/{} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(info.machine_id, host)
    ssl_sock.sendall(request.encode())

    response = b''
    while True:
        try:
            chunk = ssl_sock.recv(1024)
            if not chunk:
                break
            response += chunk
        except:
            break

    print(response.decode('utf-8', errors='replace'))
    ssl_sock.close()
    sim_close()
