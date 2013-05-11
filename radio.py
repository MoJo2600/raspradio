#!/usr/bin/python
import time
import RPi.GPIO as GPIO
import os
import signal
import sys
import threading
import datetime
from time import sleep
from RotaryEncoder import RotaryEncoder

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
		self.radio_stations = []
		self.init_playlist()
		self.current_station_index = 1
		self.refresh_suspended_till = datetime.datetime.now()
		self._switch_station = False

	def init_playlist(self):
		# clear mpc playlist
		os.system("mpc clear")

		stations_file = os.path.join(os.getcwd(), "radiostations.txt")
		f=open(stations_file, 'r')
		i = 1
		for station_raw in f:
			parts = station_raw.split("|")			
			station = { 'index': i,
				    'name': parts[0],
				    'url': parts[1]
				    } 			
			self.radio_stations.append(station)
			i += 1

			# add stations to mpc playlist
			os.system("mpc add %s" % station['url'])		

		# start playing immediately
		self.current_station_index = 1
		os.system("mpc play")
		
	def _clear_display(self):
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)			
		lcd_string(STR_PAD)
		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)			
		lcd_string(STR_PAD)

	def next(self):
		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(seconds=5)
		self.current_station_index += 1
		if self.current_station_index > len(self.radio_stations):
			self.current_station_index = 1

		self._clear_display()

		self._show_track_indicator()

		self._switch_station = True
		print("next")

	def previous(self):
		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(seconds=3)
		self.current_station_index -= 1
		if self.current_station_index < 1:
			self.current_station_index = len(self.radio_stations)

		self._clear_display()

		self._show_track_indicator()

		self._switch_station = True
		print("previous")

	def run(self):
                self._show_track_indicator()
		encoder = RotaryEncoder(3, 4, 2)		
		last_step = 0
		while 1:
			# own thread
			if self._switch_station and self.refresh_suspended_till < datetime.datetime.now():
				self._switch_station = False
#				os.system("mpc play %s" % self.current_station_index)

		        rotary_step = encoder.get_steps()
			# debounce! switch only all 100ms or so
		        if rotary_step > last_step:
				self.next()
		                last_step = rotary_step
		        elif rotary_step < last_step:
				self.previous()
		                last_step = rotary_step

			self._show_station()

#			time.sleep(0.1)

	def _show_track_indicator(self):
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string(self.radio_stations[self.current_station_index-1]['name'])
		lcd_byte(DISPLAY_LINE_2, DISPLAY_CMD)			
		track_numbers = "%d/%d" % (self.current_station_index,len(self.radio_stations)) 		
		track_text = " " * (DISPLAY_WIDTH - len(track_numbers)) 
		track_text += track_numbers
		lcd_string(track_text)

	def _show_station(self):
#		print "%s, %s" % (self.refresh_suspended_till, datetime.datetime.now())
		if self.refresh_suspended_till > datetime.datetime.now():
			return

		f=os.popen("mpc current")	

		station_text = ""
		for i in f.readlines():
        		station_text += i

		if self.current_station != station_text:
			# reset view if current track changes
			lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
			lcd_string(STR_PAD)
			self.current_char = 0
			self.current_station = station_text

		lcd_text = self.current_station[self.current_char:(self.current_char+16)]
		lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
		lcd_string(lcd_text)

		self.current_char += 1
		if self.current_char > len(self.current_station):
			self.current_char = 0

		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(milliseconds=300)


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

#	f=os.popen("mpc current")#
#	station=""
#	for i in f.readlines():
#		station += i
#	lcd_byte(DISPLAY_LINE_1, DISPLAY_CMD)
#	lcd_string(station)

	radio = InternetRadio()

#        threading.Timer(1.0, radio.show_station()).start()
	radio.run()
#        start_new_thread(radio.readinput())



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
