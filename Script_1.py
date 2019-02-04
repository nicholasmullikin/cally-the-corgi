import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import RPi.GPIO as GPIO
import time
import pigpio
import sys
import os
import signal
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

servoPIN1 = 5
servoPIN2 = 7

pi = pigpio.pi()

PAGE="""\
<html>
    <head>
    <title>picamera MJPEG streaming demo</title>
    </head>
    <body>
    <h1>PiCamera MJPEG Streaming Demo</h1>
    <button onclick='goForward();'> Go Forward </button>
    <button onclick='goBackward();'> Go Backward </button>
    <script>
    function goForward() {
    var request = new XMLHttpRequest();
    request.open('GET', '/go-forward/', true);
    request.onload = function () {
    console.log("Go forward recieved");
    }
    
    request.send();
    }
    
    function goBackward() {
    var request = new XMLHttpRequest();
    request.open('GET', '/go-backward/', true);
    request.onload = function () {
   console.log("Go backward recieved");
    }
    
    request.send();
    }
    </script>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/go-forward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            pi.set_servo_pulsewidth(servoPIN1, 800) 
            time.sleep(0.15)
        elif self.path == '/go-backward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            pi.set_servo_pulsewidth(servoPIN2, 800) 
            time.sleep(0.15)
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


address = ('', 8000)
server = StreamingServer(address, StreamingHandler)
print('serving pages')
GPIO.cleanup()
#pi.stop()

