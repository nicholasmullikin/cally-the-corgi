import io
import picamera
import pigpio
import logging
import socketserver
from threading import Condition
from http import server
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pi = pigpio.pi()
servoPIN1 = 11
pi.set_servo_pulsewidth(servoPIN1, 20000)
servoPIN2 = 13
pi.set_servo_pulsewidth(servoPIN2, 20000)

chan_list = [servoPIN1, servoPIN2]
GPIO.setup(chan_list, GPIO.OUT)

##p1 = GPIO.PWM(servoPIN1, 50) # GPIO 17 for PWM with 50Hz
##p1.start(0) # Initialization
##p2 = GPIO.PWM(servoPIN2, 50) # GPIO 27 for PWM with 50Hz
##p2.start(0) # Initialization

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
            pi.set_PWM_dutycycle(servoPIN1, 128)
            time.sleep(0.5)
        elif self.path == '/go-backward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            pi.set_PWM_dutycycle(servoPIN2, 128)
            time.sleep(0.5)
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True





address = ('', 8000)
server = StreamingServer(address, StreamingHandler)
print('serving pages')
server.serve_forever()
