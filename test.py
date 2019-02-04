#!/usr/bin/python

import RPi.GPIO as GPIO
import pigpio
import time
import sys
import os
import signal
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

servo1 = 5
servo2 = 7


pi = pigpio.pi()


def backward():
    pi.set_servo_pulsewidth(servo1, 0) 
    time.sleep(0.15)
    pi.set_servo_pulsewidth(servo2, 0)   	
    time.sleep(0.15)
while True:
    backward()
GPIO.cleanup()
pi.stop()
