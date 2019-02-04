# For camera and webpage
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import urllib
# For servos
import RPi.GPIO as GPIO
import time
import pigpio
import sys
import os
import signal
#import wave, pymedia.audio.sound as sound


# Sets the pins to putports
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

servoPIN1 = 5
servoPIN2 = 7
servoPIN3 = 2

pi = pigpio.pi()
#f= wave.open( '/home/pi/Documents/test_servo/dog_barking.wav', 'rb' )
#sampleRate= f.getframerate()
#channels= f.getnchannels()
#format= sound.AFMT_S16_LE
# snd1= sound.Output( sampleRate, channels, format )
#  s= ' '

PAGE=open("/home/pi/Documents/test_servo/page.html", "r").read()
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
        parsed_path = urllib.parse.urlparse(self.path)
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
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))

        elif parsed_path.path == '/auger-backward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.auger_backward(duration)

        elif parsed_path.path == '/auger-backward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.auger_forward(duration)

        elif parsed_path.path == '/go-forward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.forward(duration)
                
        elif parsed_path.path == '/go-forward/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.backward(duration)
            
        elif parsed_path.path == '/turn-right/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.turnleft(duration)
            
        elif parsed_path.path == '/turn-left/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            if('duration' in urllib.parse.parse_qs(parsed_path.query)):
                duration = urllib.parse.parse_qs(parsed_path.query)['duration']
                self.turnright(duration)

        elif parsed_path.path == '/stop/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            self.stop()
        elif parsed_path.path == '/bark/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len("Done".encode('utf-8')))
            self.wfile.write("Done".encode('utf-8'))
            #while len( s ):
            #    s= f.readframes( 1000 )
            #    snd1.play( s )
            #while snd1.isPlaying(): time.sleep( 0.05 )
        else:
            self.send_error(404)
            self.end_headers()
            
    def stop(self):
        pi.set_servo_pulsewidth(servoPIN2, 0) 
        pi.set_servo_pulsewidth(servoPIN1, 0)
        
    def auger_forward(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN3, 800) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN3, 0)
        
    def auger_backward(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN3, 2200) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN3, 0)        
        
    def turnright(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN2, 800) 
        pi.set_servo_pulsewidth(servoPIN1, 800) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN2, 0)
        pi.set_servo_pulsewidth(servoPIN1, 0)
    def turnleft(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN2, 2200)
        pi.set_servo_pulsewidth(servoPIN1, 2200) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN2, 0)
        pi.set_servo_pulsewidth(servoPIN1, 0)
    def forward(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN2, 800) 
        pi.set_servo_pulsewidth(servoPIN1, 2400) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN2, 0)
        pi.set_servo_pulsewidth(servoPIN1, 0)
    def backward(self, dura):
        dura = float(dura[0])
        pi.set_servo_pulsewidth(servoPIN2, 2200) 
        pi.set_servo_pulsewidth(servoPIN1, 800) 
        time.sleep(dura)
        pi.set_servo_pulsewidth(servoPIN2, 0)
        pi.set_servo_pulsewidth(servoPIN1, 0)
        

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        print("Starting server")
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        print("Started")
        server.serve_forever()
        pi.write(3, 1)
    finally:
        pi.write(3, 0)
        camera.stop_recording()
        pi.set_servo_pulsewidth(servoPIN1, 0)
        pi.set_servo_pulsewidth(servoPIN2, 0)
