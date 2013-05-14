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

class LCD:

	"""
	handles the lcd display
	"""
	# Zuordnung der GPIO Pins (ggf. anpassen)
	DISPLAY_RS = 7
	DISPLAY_E  = 8
	DISPLAY_DATA4 = 25 
	DISPLAY_DATA5 = 24
	DISPLAY_DATA6 = 23
	DISPLAY_DATA7 = 18
	
	DISPLAY_WIDTH = 16 	# characters per row
	DISPLAY_LINE_1 = 0x80 	# address of first row
	DISPLAY_LINE_2 = 0xC0 	# address of second row
	DISPLAY_CHR = True
	DISPLAY_CMD = False
	E_PULSE = 0.00005
	E_DELAY = 0.00005
	STR_PAD = " " * 16

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.DISPLAY_E, GPIO.OUT)
		GPIO.setup(self.DISPLAY_RS, GPIO.OUT)
		GPIO.setup(self.DISPLAY_DATA4, GPIO.OUT)
		GPIO.setup(self.DISPLAY_DATA5, GPIO.OUT)
		GPIO.setup(self.DISPLAY_DATA6, GPIO.OUT)
		GPIO.setup(self.DISPLAY_DATA7, GPIO.OUT)

		self.display_init()


	def display_init(self):
		self.lcd_byte(0x33,self.DISPLAY_CMD)
		self.lcd_byte(0x32,self.DISPLAY_CMD)
		self.lcd_byte(0x28,self.DISPLAY_CMD)
		self.lcd_byte(0x0C,self.DISPLAY_CMD)  
		self.lcd_byte(0x06,self.DISPLAY_CMD)
		self.lcd_byte(0x01,self.DISPLAY_CMD)  

	def lcd_clean_string(self, text):
	        text = text.replace('ä', '\xE1')
	        text = text.replace('ö', '\xEF')
	        text = text.replace('ü', '\xF5')
	        text = text.replace('Ä', '\xE1')
	        text = text.replace('Ö', '\xEF')
	        text = text.replace('Ü', '\xF5')
	        text = text.replace('ß', '\xE2')
	        return text

	def lcd_string(self, message):
		message = self.lcd_clean_string(message)
		message = message.ljust(self.DISPLAY_WIDTH," ")  
		for i in range(self.DISPLAY_WIDTH):
			self.lcd_byte(ord(message[i]),self.DISPLAY_CHR)

	def lcd_byte(self, bits, mode):
		GPIO.output(self.DISPLAY_RS, mode)
		GPIO.output(self.DISPLAY_DATA4, False)
		GPIO.output(self.DISPLAY_DATA5, False)
		GPIO.output(self.DISPLAY_DATA6, False)
		GPIO.output(self.DISPLAY_DATA7, False)
		if bits&0x10==0x10:
			GPIO.output(self.DISPLAY_DATA4, True)
		if bits&0x20==0x20:
			GPIO.output(self.DISPLAY_DATA5, True)
		if bits&0x40==0x40:
		  GPIO.output(self.DISPLAY_DATA6, True)
		if bits&0x80==0x80:
		  GPIO.output(self.DISPLAY_DATA7, True)
		time.sleep(self.E_DELAY)    
		GPIO.output(self.DISPLAY_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.DISPLAY_E, False)  
		time.sleep(self.E_DELAY)      
		GPIO.output(self.DISPLAY_DATA4, False)
		GPIO.output(self.DISPLAY_DATA5, False)
		GPIO.output(self.DISPLAY_DATA6, False)
		GPIO.output(self.DISPLAY_DATA7, False)
		if bits&0x01==0x01:
		  GPIO.output(self.DISPLAY_DATA4, True)
		if bits&0x02==0x02:
		  GPIO.output(self.DISPLAY_DATA5, True)
		if bits&0x04==0x04:
		  GPIO.output(self.DISPLAY_DATA6, True)
		if bits&0x08==0x08:
		  GPIO.output(self.DISPLAY_DATA7, True)
		time.sleep(self.E_DELAY)    
		GPIO.output(self.DISPLAY_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.DISPLAY_E, False)  
		time.sleep(self.E_DELAY)   
