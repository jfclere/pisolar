#!/usr/bin/python
'''
	Based on the work off:
	Author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO
import time
from picamera2 import Picamera2
import subprocess

picam2 = Picamera2()

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print("do_GET")
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					# capture main.
					np_array = picam2.capture_array()
					# convert to cv2 internal format.
					imgRGB = cv2.cvtColor(np_array, cv2.COLOR_BGRA2RGB)
					img_bytes = cv2.imencode('.jpg', imgRGB)[1].tobytes()
					print("sending saved image...")
					self.wfile.write(b'--')
					self.wfile.write(b"--jpgboundary")
					self.wfile.write(b'\r\n')
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(len(img_bytes)))
					self.end_headers()
					self.wfile.write(img_bytes)
					time.sleep(0.05)
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html'):
			print("html request")
			host = self.headers.get('Host')
			print(host)
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes('<html><head></head><body>', "utf-8"))
			self.wfile.write(bytes('<img src="http://' + host + '/cam.mjpg"/>', "utf-8"))
			self.wfile.write(bytes('</body></html>', "utf-8"))
			return
		if self.path.endswith('Down'):
 			# Call the Down script...
			self.DoCmd("Down")
			return
		if self.path.endswith('Up'):
 			# Call the Up script...
			self.DoCmd("Up")
			return
		if self.path.endswith('Right'):
 			# Call the Up script...
			self.DoCmd("Right")
			return
		if self.path.endswith('Left'):
 			# Call the Up script...
			self.DoCmd("Left")
			return
		self.send_error(404, message=None, explain=None)
		host = self.headers.get('Host')
		print(host)
	def DoCmd(self, cmd):
		# run /home/pi/pisolar/servos90.py cmd
		subprocess.run(["/home/pi/pisolar/servos90.py", cmd])
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write(bytes('<html><head></head><body>', "utf-8"))
		self.wfile.write(bytes('<p>' + cmd + '!</p>', "utf-8"))
		self.wfile.write(bytes('</body></html>', "utf-8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	# - Selected unicam format: 4656x3496-pRAA
	preview_config = picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
	picam2.configure(preview_config)

	picam2.start()

	global img
	try:
		server = ThreadedHTTPServer(('', 8080), CamHandler)
		print("server started")
		server.serve_forever()
	except KeyboardInterrupt:
		picam2.close()
		server.socket.close()

if __name__ == '__main__':
	main()

