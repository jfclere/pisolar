#!/usr/bin/python3

# Python ssl (OpenSSL) does TLS via MemoryBIO.
# SIM7028 raw TCP: AT+CIPSEND to send, AT+CIPRXGET=3 to receive (hex mode).

import time
import serial
import sys
import ssl

ser = None

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
            if line == 'OK' or line == 'ERROR' or line.startswith('CONNECT'):
                break
        else:
            time.sleep(0.05)
    return lines

def waitline(timeout=10):
    """Read one line from serial"""
    end = time.time() + timeout
    while time.time() < end:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                return line
        time.sleep(0.05)
    return ''

def sim_open(host, port):
    sendcmd('AT+CEREG?')
    sendcmd('AT+CIPCLOSE=0')
    sendcmd('AT+NETCLOSE')
    time.sleep(1)
    sendcmd('AT+CIPMODE=0')
    # Try manual receive mode (hex-safe)
    res = sendcmd('AT+CIPRXGET=1')
    rxget_ok = any('OK' in l for l in res)
    if not rxget_ok:
        print("CIPRXGET not supported, falling back to +IPD mode")
    sendcmd('AT+NETOPEN', timeout=10)
    time.sleep(2)
    sendcmd('AT+IPADDR')
    res = sendcmd('AT+CIPOPEN=0,"TCP","{}",{}'.format(host, port), timeout=30)
    for line in res:
        if '+CIPOPEN: 0,0' in line:
            print("TCP connected to {}:{}".format(host, port))
            return rxget_ok
    start = time.time()
    while time.time() - start < 30:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            print("<<< " + line)
            if '+CIPOPEN: 0,0' in line:
                print("TCP connected to {}:{}".format(host, port))
                return rxget_ok
            if 'ERROR' in line:
                break
        time.sleep(0.05)
    print("TCP connection failed")
    return None

def sim_close():
    sendcmd('AT+CIPCLOSE=0')
    sendcmd('AT+NETCLOSE')

def sim_send(data):
    """Send binary data via AT+CIPSEND"""
    ser.write('AT+CIPSEND=0,{}\r\n'.format(len(data)).encode())
    end = time.time() + 5
    while time.time() < end:
        if ser.in_waiting > 0:
            buf = ser.read(ser.in_waiting)
            if b'>' in buf:
                break
            if b'ERROR' in buf:
                print("CIPSEND: ERROR")
                return False
        time.sleep(0.02)
    else:
        print("CIPSEND: no > prompt")
        return False
    ser.write(data)
    ser.flush()
    # Wait for +CIPSEND confirmation
    end = time.time() + 10
    while time.time() < end:
        line = waitline(timeout=2)
        if not line:
            continue
        if 'CIPSEND' in line:
            print("SND: " + line)
            return True
        if 'ERROR' in line:
            return False
    print("CIPSEND: timeout")
    return False

def sim_recv_rxget(timeout=30):
    """Receive data using AT+CIPRXGET=3 (hex mode) — no binary corruption"""
    end = time.time() + timeout
    avail = 0

    # Drain any pending serial data (notifications we missed)
    time.sleep(1)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print("DRAIN: " + line)

    # Poll for available data
    while time.time() < end:
        res = sendcmd('AT+CIPRXGET=4,0', timeout=2)
        for r in res:
            if '+CIPRXGET: 4' in r:
                parts = r.split(',')
                if len(parts) >= 2:
                    try:
                        avail = int(parts[-1].strip())
                    except ValueError:
                        pass
        if avail > 0:
            break
        time.sleep(1)

    if avail <= 0:
        print("RXGET: no data available")
        return b''

    print("RXGET: {} bytes available".format(avail))

    # Read in hex mode, max ~500 bytes per request (1000 hex chars)
    result = b''
    while avail > 0:
        chunk_size = min(avail, 500)
        ser.write('AT+CIPRXGET=3,0,{}\r\n'.format(chunk_size).encode())
        time.sleep(0.3)
        hexdata = ''
        got_header = False
        actual = 0
        end2 = time.time() + 5
        while time.time() < end2:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line.startswith('+CIPRXGET: 3'):
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            actual = int(parts[2].strip())
                        except ValueError:
                            pass
                    got_header = True
                    continue
                if got_header and line and line != 'OK':
                    hexdata += line
                if line == 'OK':
                    break
            time.sleep(0.02)

        if hexdata:
            try:
                result += bytes.fromhex(hexdata)
            except ValueError:
                print("RXGET: hex decode error: " + hexdata[:40])
                break
        avail -= actual if actual > 0 else chunk_size
        if actual == 0:
            break

    print("RXGET: got {} bytes".format(len(result)))
    return result

serial_buf = b''

def serial_read(n, timeout=5):
    """Read n bytes from serial, using blocking read with timeout"""
    old_timeout = ser.timeout
    ser.timeout = timeout
    data = ser.read(n)
    ser.timeout = old_timeout
    return data

def sim_recv_ipd(timeout=30):
    """Fallback: wait for +IPD data from serial"""
    global serial_buf
    end = time.time() + timeout
    while time.time() < end:
        if ser.in_waiting > 0:
            serial_buf += ser.read(ser.in_waiting)
        elif not serial_buf or b'+IPD' not in serial_buf:
            b = serial_read(1, timeout=1)
            if b:
                serial_buf += b
                if ser.in_waiting > 0:
                    serial_buf += ser.read(ser.in_waiting)
            continue

        ipd_idx = serial_buf.find(b'+IPD')
        if ipd_idx < 0:
            continue
        after = serial_buf[ipd_idx + 4:]
        if b'\r\n' not in after:
            serial_buf += serial_read(1, timeout=1)
            continue

        nl = after.find(b'\r\n')
        try:
            datalen = int(after[:nl])
        except ValueError:
            serial_buf = serial_buf[ipd_idx + 4:]
            continue

        data_start = nl + 2
        have = len(after) - data_start
        retries = 0
        while have < datalen and retries < 3:
            chunk = serial_read(min(datalen - have, 512), timeout=1)
            if chunk:
                serial_buf += chunk
                after = serial_buf[ipd_idx + 4:]
                have = len(after) - data_start
            else:
                retries += 1

        take = min(have, datalen)
        payload = after[data_start:data_start + take]
        serial_buf = serial_buf[ipd_idx + 4 + data_start + take:]
        print("IPD: {}/{} bytes".format(len(payload), datalen))
        return payload

    print("sim_recv: timeout")
    return b''

# Will be set by main
use_rxget = False

def sim_recv(timeout=30):
    if use_rxget:
        return sim_recv_rxget(timeout)
    return sim_recv_ipd(timeout)

def tls_handshake(host):
    """Do TLS handshake using MemoryBIO + SIM7028"""
    incoming = ssl.MemoryBIO()
    outgoing = ssl.MemoryBIO()

    ctx = ssl.create_default_context()
    sslobj = ctx.wrap_bio(incoming, outgoing, server_hostname=host)

    for attempt in range(20):
        try:
            sslobj.do_handshake()
            print("TLS handshake complete: " + sslobj.version())
            return sslobj, incoming, outgoing
        except ssl.SSLWantReadError:
            data = outgoing.read()
            if data:
                print("TLS->SIM: {} bytes".format(len(data)))
                if not sim_send(data):
                    print("TLS handshake: send failed")
                    return None, None, None
            sim_data = sim_recv(timeout=10)
            if sim_data:
                print("SIM->TLS: {} bytes".format(len(sim_data)))
                incoming.write(sim_data)
            else:
                print("TLS handshake: no data from SIM")
                return None, None, None
        except ssl.SSLError as e:
            print("TLS error: " + str(e))
            return None, None, None

def flush_outgoing(outgoing):
    """Send any pending outgoing TLS data (e.g. post-handshake)"""
    data = outgoing.read()
    if data:
        print("TLS->SIM flush: {} bytes".format(len(data)))
        sim_send(data)

def tls_send(sslobj, outgoing, data):
    """Send data over TLS"""
    sslobj.write(data)
    encrypted = outgoing.read()
    if encrypted:
        return sim_send(encrypted)
    return True

def tls_recv(sslobj, incoming, outgoing, timeout=10):
    """Receive data over TLS, may need multiple sim_recv calls"""
    result = b''
    for _ in range(10):
        sim_data = sim_recv(timeout=timeout)
        if not sim_data:
            break
        incoming.write(sim_data)
        try:
            chunk = sslobj.read(16384)
            if chunk:
                result += chunk
        except ssl.SSLWantReadError:
            flush_outgoing(outgoing)
            continue
        except ssl.SSLError as e:
            print("TLS read error: " + str(e))
            break
        flush_outgoing(outgoing)
        if result:
            break
    return result

if __name__ == '__main__':
    host = "jfclere.myddns.me"
    port = 443
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    sendcmd('AT')

    rxget = sim_open(host, port)
    if rxget is None:
        print("Connection failed")
        sys.exit(1)
    use_rxget = rxget
    print("Receive mode: " + ("CIPRXGET hex" if use_rxget else "+IPD"))

    sslobj, incoming, outgoing = tls_handshake(host)
    if not sslobj:
        print("TLS handshake failed")
        sim_close()
        sys.exit(1)

    from AT_nodeinfo import nodeinfo
    info = nodeinfo()
    request = "GET /machines/{} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(info.machine_id, host)
    flush_outgoing(outgoing)
    tls_send(sslobj, outgoing, request.encode())

    response = tls_recv(sslobj, incoming, outgoing)
    print(response.decode('utf-8', errors='replace'))

    sim_close()
