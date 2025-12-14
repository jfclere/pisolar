import time
import socket
import select
import ssl
import base64

# linux version of the wifi from picow
# Read configuration.
class wifi():
 # read lets-encrypt-r3.der
 def getcadata(self):
   file = open('lets-encrypt-r3.der', 'rb')
   cadata = file.read()
   file.close()
   return bytes(cadata)

# wait for data or timeout
 def readwait(self, s, mytime):
  poller = select.poll()
  poller.register(s, select.POLLIN)
  res = poller.poll(mytime)  # time in milliseconds
  if not res:
    #timeout
    print("timeout!")
    s.close()
    return False
  return True

 # connect and send message to the server
 # mess the mess
 # name the URL
 def sendserver(self, mess, name, hostname, port, login, password):

  print("sendserver: " + name)

  ai = socket.getaddrinfo(hostname, port)
  # print("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  # print("Connect address:", addr)
  s.connect(addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  context = ssl.create_default_context()
  context.load_verify_locations(cadata=cadata)
  #context.check_hostname = False
  #context.verify_mode = ssl.CERT_NONE
  s = context.wrap_socket(s, server_hostname=hostname) #, cadata=cadata)
  # print(s)

  # write it
  s.write(bytes("PUT " + name + " HTTP/1.1\r\n", 'utf-8'))
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  userpassword = login + ":" + password
  autho=b"Authorization: Basic " + base64.b64encode(bytes(userpassword, 'utf-8'))
  # print(autho)
  s.write(autho)
  s.write(b"\r\n")
  contentlength = "Content-Length: " + str(len(mess))
  # print(contentlength)
  s.write(bytes(contentlength, 'utf-8'))
  s.write(b"\r\n")
  s.write(b"Expect: 100-continue\r\n")
  s.write(b"\r\n")

  # Print the response (b'HTTP/1.1 100 Continue\r\n\r\n')
  # print(s.read(25))

  # Write the content of the temp.txt file
  s.write(mess)

  if not self.readwait(s, 50000):
    raise Exception("getfilefromserver: timeout")

  resp = s.read(512)

  # print(resp)

  # done close the socket
  s.close()


 # connect and return a socket to the server
 # connect and receive a file from server
 def getfromserver(self, name, hostname, port):

  print("getfromserver: " + name)

  ai = socket.getaddrinfo(hostname, port)
  # print("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  s = socket.socket()
  # print("Connect address:", addr)
  s.connect(addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  context = ssl.SSLContext(cadata=cadata)
  context.check_hostname = False
  context.verify_mode = ssl.CERT_NONE
  s = context.wrap_socket(s, server_hostname=hostname) #, cadata=cadata)
  # print(s)

  # write request
  s.write(b"GET /")
  s.write(bytearray(name, 'utf8'))
  s.write(b" HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  s.write(b"\r\n")
  return s

 # connect and receive a file from server
 def getfilefromserver(self, name):
  s = self.getfromserver("/webdav/" + name)

  if not self.readwait(s, 50000):
    raise Exception("getfilefromserver: timeout")

  resp = s.read(512)
  string = str(resp, "utf-8")
  headers = string.split("\r\n")
  l = 0
  size = 0
  indata = False
  f = open(name, "w")
  for header in headers:
    if "Content-Length:" in header:
      # Length to read.
      cl = header.split(": ")
      print(cl[1])
      l = int(cl[1])
      continue
    if l>0 and not indata:
      # We skip until empty line
      if len(header) == 0:
        indata = True
        continue
    if indata:
      # Store the line in a file
      print("data: " + header)
      f.write(header)
      size = size + len(header)
      if size == l:
        break # Done!
  while size < l:
    if not self.readwait(s, 50000):
      f.close()
      raise Exception("getfilefromserver: timeout")
    resp = s.read(512)
    f.write(resp)
    size = size + len(resp)
  f.close()
  # done close the socket
  s.close()

 # connect and send a get (STATUS) to server
 def sendstatustoserver(self, name, hostname, port):

  print("sendstatustoserver: " + hostname + ":" + str(port) + " " + name);
  
  status = self.wlan.ifconfig()
  # print("status: " + status[0])
  # status[3] = '8.8.8.8'
  #if status[2] == status[3]:
  #  print("status: " + status[2])
  #  print("status: " + status[3])
  #  self.wlan.ifconfig((status[0], status[1], status[2], '8.8.8.8'))
  # print("status: " + str(self.wlan.status()))
  # print("status: " + str(self.wlan.isconnected()))
  #status = self.wlan.ifconfig()
  # print("status: (3)" + status[3])
  ai = socket.getaddrinfo('jfclere.myddns.me', self.port)
  # print("Address infos:", ai)
  addr = ai[0][-1]

  # Create a socket and make a HTTP request
  ## s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s = socket.socket()
  s.connect(addr)
  # print(s)
  # print("Connect address:", addr)
  # cadata=CA certificate chain (in DER format)
  cadata = self.getcadata()
  s = ssl.wrap_socket(s, cadata=cadata)
  # print(s)

  # write request
  s.write(b"GET ")
  s.write(bytearray(name, 'utf8'))
  s.write(b" HTTP/1.1\r\n")
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  s.write(b"\r\n")

  print("waiting response...")
  if not self.readwait(s, 50000):
    return 0
  resp = s.read(512)
  string = str(resp, "utf-8")
  headers = string.split("\r\n")
  for header in headers:
    print("header: " + header)
    if "HTTP/" in header:
      # Length to read.
      cl = header.split(" ")
      print(cl[1])
      l = int(cl[1])
      s.close()
      return l
  # done close the socket
  s.close()
  return 0

 # create a collection / directory on the server
 def createdirserver(self, name, hostname, port, login, password):
  print("createdirserver: " + hostname + ":" + str(port) + " " + name);
  ai = socket.getaddrinfo(hostname, port)
  addr = ai[0][-1]
  s = socket.socket()
  s.connect(addr)
  cadata = self.getcadata()
  context = ssl.create_default_context()
  context.load_verify_locations(cadata=cadata)
  s = context.wrap_socket(s, server_hostname=hostname) #, cadata=cadata)
  s.write(bytes("MKCOL " + name + " HTTP/1.1\r\n", 'utf-8'))
  s.write(b"Host: jfclere.myddns.me\r\n")
  s.write(b"User-Agent: picow/0.0.0\r\n")
  userpassword = login + ":" + password
  autho=b"Authorization: Basic " + base64.b64encode(bytes(userpassword, 'utf-8'))
  s.write(autho)
  s.write(b"\r\n")
  s.write(b"\r\n")

  # just check we get a response from the moment
  if not self.readwait(s, 50000):
    raise Exception("createdirserver: timeout")
  resp = s.read(512)
  # print(resp)
  s.close()
