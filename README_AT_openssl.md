# AT_openssl.py

TLS over SIM7028 raw TCP, with Python's `ssl` module doing all the crypto.

## Architecture

```
Application (HTTP request/response)
        |
   ssl.SSLObject  (TLS encrypt/decrypt via OpenSSL)
        |
   ssl.MemoryBIO  (in-memory buffers, no sockets)
        |
   SIM7028 AT commands  (raw TCP transport via serial)
        |
   NB-IoT network
```

The SIM7028 provides a raw TCP socket. Python's `ssl.MemoryBIO` handles TLS without needing OS sockets -- data is shuttled between the MemoryBIO buffers and the SIM7028 serial port.

## Key problem solved: binary data corruption

The SIM7028's default receive mode (`+IPD` push notifications) corrupts binary data by stripping `\r\n` bytes. A 1340-byte TLS record would arrive as ~700-990 bytes.

The fix: `AT+CIPRXGET=1` enables manual receive mode. Data is pulled with `AT+CIPRXGET=3,0,<len>` which returns hex-encoded bytes. Hex is ASCII-safe, so no bytes are lost.

## Data flow

### Sending (works with standard AT+CIPSEND)
1. `ssl.SSLObject.write()` encrypts application data into the outgoing MemoryBIO
2. Read encrypted bytes from outgoing BIO
3. `AT+CIPSEND=0,<len>` sends them as raw TCP

### Receiving (hex mode via AT+CIPRXGET)
1. Poll `AT+CIPRXGET=4,0` until data is available
2. Pull data with `AT+CIPRXGET=3,0,<len>` (returns hex string)
3. Decode hex back to binary
4. Write binary into incoming MemoryBIO
5. `ssl.SSLObject.read()` decrypts it

### TLS handshake
Loop calling `sslobj.do_handshake()` which raises `SSLWantReadError` until complete. On each iteration, send outgoing BIO data to SIM and feed received SIM data to incoming BIO.

### TLS 1.3 post-handshake
After the handshake, TLS 1.3 may queue outgoing data (NewSessionTicket responses). `flush_outgoing()` sends these before application data exchange.

## AT commands used

| Command | Purpose |
|---------|---------|
| `AT+CIPMODE=0` | Buffered (non-transparent) mode |
| `AT+CIPRXGET=1` | Enable manual receive mode |
| `AT+NETOPEN` | Open network |
| `AT+CIPOPEN=0,"TCP",host,port` | Open raw TCP connection |
| `AT+CIPSEND=0,<len>` | Send binary data |
| `AT+CIPRXGET=4,0` | Query available received bytes |
| `AT+CIPRXGET=3,0,<len>` | Read received data as hex |
| `AT+CIPCLOSE=0` | Close TCP connection |
| `AT+NETCLOSE` | Close network |

## Usage

```
python3 AT_openssl.py [host] [port]
```

Defaults to `jfclere.myddns.me:443`. Reads machine config from `/etc/machine-id` and credentials from `~/.netrc`.
