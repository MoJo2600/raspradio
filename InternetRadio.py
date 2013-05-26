# -*- coding: utf-8 -*-
import re
import time
import os
import signal
import sys
import threading
import Queue
import datetime
from time import sleep

CURRENT_STATION = ""
CURRENT_CHAR = 0
LAST_STATION_FILE = ".laststation"
STATIONS_FILE = "radiostations.txt"
WAIT_FOR_STATION_CHANGE = 2.0    # Wait 2 sek before switching stations

class MPCClient(threading.Thread):
    """
    handles the mpc commands in an own thread
    the interrupts got disconnected due to the time the switching needed
    """
    CMD_CLEAR = "mpc clear"
    CMD_ADD = "mpc add %s"
    CMD_PLAY = "mpc play"
    CMD_STOP = "mpc stop"
    CMD_PLAY_INDEX = "mpc play %s"

    command_queue = Queue.Queue()
    lock = threading.Lock()

    def run(self):
        while True:
            try:
                command = MPCClient.command_queue.get()
                os.system(command)
                MPCClient.command_queue.task_done()
            except Queue.Empty:
                pass


class InternetRadio:
    """
    Class that creates a InternetRadio with help of mpc
    """
    def __init__(self, frame):
        self._frame = frame

        self.current_station_text = ""
        self.radio_stations = []

        self.mpcclient = MPCClient()
        self.mpcclient.setDaemon(True)
        self.mpcclient.start()

        self._switch_timer = None
        self._show_station_timer = None

        self.init_playlist()

    def init_playlist(self):
        """
        Loads all stations from radiostations.txt into mpd playlist
        """
        # clear mpc playlist
        MPCClient.command_queue.put(MPCClient.CMD_CLEAR)

        stations_file = os.path.join(os.getcwd(), STATIONS_FILE)
        f = open(stations_file, 'r')
        i = 1
        for station_raw in f:
            parts = station_raw.split("|")
            station = {
                'index': i,
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

        self._switch_station()

    def _switch_station(self):
        """
        Show station information and switch station after given time
        """
        self._show_station()
        self._show_track_indicator()

        if self._switch_timer is not None:
            self._switch_timer.cancel()
        self._switch_timer = threading.Timer(WAIT_FOR_STATION_CHANGE, self._do_switch_station)
        self._switch_timer.start()

    def _do_switch_station(self):
        """
        Executes the switch after a given time
        """
        MPCClient.command_queue.put(MPCClient.CMD_PLAY_INDEX % self.current_station_index)
        self._show_station()
        self._store_last_station()

    def next(self):
        """
        Switches to the next station
        """
        self.current_station_index += 1
        if self.current_station_index > len(self.radio_stations):
            self.current_station_index = 1

        self._switch_station()

    def previous(self):
        """
        Switches to the previous station
        """
        self.current_station_index -= 1
        if self.current_station_index < 1:
            self.current_station_index = len(self.radio_stations)

        self._switch_station()

    def start(self):
        """
        Starts the radio
        """
        self._switch_station()

    def stop(self):
        """
        Stops the radio
        """
        if self._switch_timer is not None:
            self._switch_timer.cancel()
        if self._show_station_timer is not None:
            self._show_station_timer.cancel()
        MPCClient.command_queue.put(MPCClient.CMD_STOP)

    def _store_last_station(self):
        """
        save the last selected radio station for convenience
        """
        f = open(LAST_STATION_FILE, 'w')
        f.write("%s" % self.current_station_index)
        f.close()

    def _show_track_indicator(self):
        """
        Shows the indicator for the current station
        """
        self._frame.widget_title_line.set_contents(self.radio_stations[self.current_station_index-1]['name'])
        track_numbers = "%d/%d" % (self.current_station_index, len(self.radio_stations))
        self._frame.widget_track_line.set_contents(track_numbers)

    def _show_station(self):
        """
        Reads information about the current station from mpc
        """
        # TODO should be implemented in MPCClient
        station_text = ""
        f = os.popen("mpc current")
        for i in f.readlines():
            station_text += i

        station_text = re.sub("[^0-9a-zA-Z äöüÄÖÜ\-+:]", "", station_text)

        if self.current_station_text != station_text:
            self.current_station_text = station_text
            self._frame.widget_title_line.set_contents(self.current_station_text)

        if self._show_station_timer is not None:
            self._show_station_timer.cancel()

        self._show_station_timer = threading.Timer(1.0, self._show_station)
        self._show_station_timer.start()
