#!/usr/bin/python
import time
import RPi.GPIO as GPIO
import os
import signal
import sys
import threading
from time import sleep

# Zuordnung der GPIO Pins (ggf. anpassen)
DISPLAY_RS = 7
DISPLAY_E  = 8
DISPLAY_DATA4 = 25 
DISPLAY_DATA5 = 24
DISPLAY_DATA6 = 23
DISPLAY_DATA7 = 18

DISPLAY_WIDTH = 16 	# Zeichen je Zeile
DISPLAY_LINE_1 = 0x80 	# Adresse der ersten Display Zeile
DISPLAY_LINE_2 = 0xC0 	# Adresse der zweiten Display Zeile
DISPLAY_CHR = True
DISPLAY_CMD = False
E_PULSE = 0.00005
E_DELAY = 0.00005
STR_PAD = " " * 16

CURRENT_STATION = ""
CURRENT_CHAR = 0

def signal_handler(signal, frame):
        print 'Closing Internet Radio!'
	GPIO.cleanup()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class InternetRadio:


	def __init__(self):
		self.current_station = ""
		self.current_char = 0
		self.playlist = {}
		self.init_playlist()

	def init_playlist(self):
		f=os.popen("radiostations.txt")
		i = 1
		for station_raw in f.readlines():
			parts = station_raw.split("|")			
			station = { index: i,
				    name: parts[0],
				    url: parts[1]
				    } 			
			self.playlist.append(station)
			i += 1
		# clear mpc playlist
		os.system("mpc "		
		

	def show_station(self):
		f=os.popen("mpc current")	
		station_text = ""
		for i in f.readlines():
        		station_text += i

		if station_text != self.current_station:
			self.current_station = station_text
			lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
			lcd_string(STR_PAD)
			self.current_char = 0

		lcd_text = self.current_station[self.current_char:(self.current_char+16)]
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string(lcd_text)

		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
		index = self.playlist.index(station_text)
		track_text = "%s/%s" % (index,len(self.playlist)) 
		track_text = " " * (DISPLAY_WIDTH - len(track_text)) + track_text

		lcd_string(track_text)

		self.current_char += 1
		if self.current_char > DISPLAY_WIDTH:
			self.current_char = 0

		sleep(0.3)
		self.show_station()

def main():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(DISPLAY_E, GPIO.OUT)
	GPIO.setup(DISPLAY_RS, GPIO.OUT)
	GPIO.setup(DISPLAY_DATA4, GPIO.OUT)
	GPIO.setup(DISPLAY_DATA5, GPIO.OUT)
	GPIO.setup(DISPLAY_DATA6, GPIO.OUT)
	GPIO.setup(DISPLAY_DATA7, GPIO.OUT)

	display_init()

	#lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
	#lcd_string("Schnatterente")
	#lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
	#lcd_string("Nak nak nak!")

	#time.sleep(5)

	#lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
	#lcd_string("Dein Display")
	#lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)
	#lcd_string("funktioniert! :)")	

	f=os.popen("mpc current")
	station=""
	for i in f.readlines():
		station += i
	lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
	lcd_string(station)

	radio = InternetRadio()

#        threading.Timer(1.0, radio.show_station()).start()
	radio.show_station()		
#	while 1: #
#		print "looping"
#		time.sleep(20)


def display_init():
	lcd_byte(0x33,DISPLAY_CMD)
	lcd_byte(0x32,DISPLAY_CMD)
	lcd_byte(0x28,DISPLAY_CMD)
	lcd_byte(0x0C,DISPLAY_CMD)  
	lcd_byte(0x06,DISPLAY_CMD)
	lcd_byte(0x01,DISPLAY_CMD)  

def lcd_string(message):
	message = message.ljust(DISPLAY_WIDTH," ")  
	for i in range(DISPLAY_WIDTH):
	  lcd_byte(ord(message[i]),DISPLAY_CHR)

def lcd_byte(bits, mode):
	GPIO.output(DISPLAY_RS, mode)
	GPIO.output(DISPLAY_DATA4, False)
	GPIO.output(DISPLAY_DATA5, False)
	GPIO.output(DISPLAY_DATA6, False)
	GPIO.output(DISPLAY_DATA7, False)
	if bits&0x10==0x10:
	  GPIO.output(DISPLAY_DATA4, True)
	if bits&0x20==0x20:
	  GPIO.output(DISPLAY_DATA5, True)
	if bits&0x40==0x40:
	  GPIO.output(DISPLAY_DATA6, True)
	if bits&0x80==0x80:
	  GPIO.output(DISPLAY_DATA7, True)
	time.sleep(E_DELAY)    
	GPIO.output(DISPLAY_E, True)  
	time.sleep(E_PULSE)
	GPIO.output(DISPLAY_E, False)  
	time.sleep(E_DELAY)      
	GPIO.output(DISPLAY_DATA4, False)
	GPIO.output(DISPLAY_DATA5, False)
	GPIO.output(DISPLAY_DATA6, False)
	GPIO.output(DISPLAY_DATA7, False)
	if bits&0x01==0x01:
	  GPIO.output(DISPLAY_DATA4, True)
	if bits&0x02==0x02:
	  GPIO.output(DISPLAY_DATA5, True)
	if bits&0x04==0x04:
	  GPIO.output(DISPLAY_DATA6, True)
	if bits&0x08==0x08:
	  GPIO.output(DISPLAY_DATA7, True)
	time.sleep(E_DELAY)    
	GPIO.output(DISPLAY_E, True)  
	time.sleep(E_PULSE)
	GPIO.output(DISPLAY_E, False)  
	time.sleep(E_DELAY)   

if __name__ == '__main__':
	main()
