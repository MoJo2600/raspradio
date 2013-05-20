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

CURRENT_STATION = ""
CURRENT_CHAR = 0

LAST_STATION_FILE = ".laststation"

WAIT_FOR_STATION_CHANGE = 200    # Wait 2 sek before switcheng stations


class MPCClient(threading.Thread):
    """
	handles the mpc commands in an own thread
	the interrupts got disconnected due to the time the switching needed
	"""
    CMD_CLEAR = "mpc clear"
    CMD_ADD = "mpc add %s"
    CMD_PLAY = "mpc play"
    CMD_PLAY_INDEX = "mpc play %s"

    command_queue = Queue.Queue()
    lock = threading.Lock()

    def run(self):
        while True:
            command = MPCClient.command_queue.get()
            os.system(command)
            MPCClient.command_queue.task_done()

class InternetRadio:
	
	def __init__(self, lcd):
		self.current_station = ""
		self.current_char = 0
		self.radio_stations = []
		self.refresh_suspended_till = datetime.datetime.now()
		self._switch_station = False
		self.lcd = lcd

		self.mpcclient = MPCClient()
		self.mpcclient.setDaemon(True) 
		self.mpcclient.start()

		self.init_playlist()

	def init_playlist(self):
		"""
		loads all stations from radiostations.txt into mpd playlist
		"""
		# clear mpc playlist
		MPCClient.command_queue.put(MPCClient.CMD_CLEAR)

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
			MPCClient.command_queue.put(MPCClient.CMD_ADD % station['url'])

		# start playing immediately
		self.current_station_index = 1
		try:
			with open(LAST_STATION_FILE) as f: 
				index = int(f.read())
				if index > 0 and index <= len(self.radio_stations):
					self.current_station_index = index
		except IOError:
			print 'No last station file, playing first'
		except ValueError:
			print 'last station file corrupted'
			os.remove(LAST_STATION_FILE)

		self._show_track_indicator()
		MPCClient.command_queue.put(MPCClient.CMD_PLAY_INDEX % self.current_station_index)
		
	def _clear_display(self):
		self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_1, self.lcd.DISPLAY_CMD)			
		self.lcd.lcd_string(self.lcd.STR_PAD)
		self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_2, self.lcd.DISPLAY_CMD)			
		self.lcd.lcd_string(self.lcd.STR_PAD)

	def next(self):
		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(seconds=5)

		self.current_station_index += 1
		if self.current_station_index > len(self.radio_stations):
			self.current_station_index = 1

		self._clear_display()
		self._show_track_indicator()
		self._switch_station = True

	def previous(self):
		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(seconds=3)

		self.current_station_index -= 1
		if self.current_station_index < 1:
			self.current_station_index = len(self.radio_stations)

		self._clear_display()
		self._show_track_indicator()
		self._switch_station = True

	def _store_last_station(self):
		"""
		save the last selected radio station for convenience
		"""
		f=open(LAST_STATION_FILE, 'w')
		f.write("%s" % self.current_station_index)

	def run(self):
                self._show_track_indicator()
		encoder = RotaryEncoder(3, 4, 2)		
		last_step = 0
		while 1:
			if self._switch_station and self.refresh_suspended_till < datetime.datetime.now():
				self._switch_station = False
				MPCClient.command_queue.put(MPCClient.CMD_PLAY_INDEX % self.current_station_index)
				self._store_last_station()

		        rotary_step = encoder.get_steps()

			# debounce! switch only all 100ms or so
		        if rotary_step > last_step:
				self.next()
		                last_step = rotary_step
		        elif rotary_step < last_step:
				self.previous()
		                last_step = rotary_step

			self._show_station()

			time.sleep(0.001)

	def _show_track_indicator(self):
		self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_1, self.lcd.DISPLAY_CMD)
		self.lcd.lcd_string(self.radio_stations[self.current_station_index-1]['name'])
		self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_2, self.lcd.DISPLAY_CMD)			
		track_numbers = "%d/%d" % (self.current_station_index, len(self.radio_stations)) 		
		track_text = " " * (self.lcd.DISPLAY_WIDTH - len(track_numbers)) 
		track_text += track_numbers
		self.lcd.lcd_string(track_text)

	def _show_station(self):
		if self.refresh_suspended_till > datetime.datetime.now():
			return
		# TODO should be implemented in MPCClient
		f=os.popen("mpc current")	

		station_text = ""
		for i in f.readlines():
        		station_text += i

		if self.current_station != station_text:
			# reset view if current track changes
			self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_1, self.lcd.DISPLAY_CMD)
			self.lcd.lcd_string(self.lcd.STR_PAD)
			self.current_char = 0
			self.current_station = station_text

		lcd_text = self.current_station[self.current_char:(self.current_char+16)]
		self.lcd.lcd_byte(self.lcd.DISPLAY_LINE_1, self.lcd.DISPLAY_CMD)
		self.lcd.lcd_string(lcd_text)

		self.current_char += 1
		if self.current_char > len(self.current_station):
			self.current_char = 0

		self.refresh_suspended_till = datetime.datetime.now() + datetime.timedelta(milliseconds=WAIT_FOR_STATION_CHANGE)
