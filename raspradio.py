#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
import os
import signal
import sys
import threading
import Queue
import datetime
from time import sleep
from RotaryEncoder import RotaryEncoder
from LCD import LCD
from InternetRadio import InternetRadio

def signal_handler(signal, frame):
	"""
	clean up before closing application
	"""
        print 'Closing Internet Radio!'
	GPIO.cleanup()
        sys.exit(0)
	MPCClient.command_queue.join()
# Connect singal_handler callback to sigint
signal.signal(signal.SIGINT, signal_handler)

def main():
	lcd = LCD()
	radio = InternetRadio(lcd)
	radio.run()

if __name__ == '__main__':
	main()
