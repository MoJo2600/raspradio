#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
import sys
from threading import Timer
from InternetRadio import InternetRadio
from lcd.devices.Generic import MockCharacterDisplay
from lcd.ui import frame
from lcd.ui import widget
from lcd.ui.ui import LcdUi


def signal_handler(signal, frame):
    """
    clean up before closing application
    """
    print 'Closing Internet Radio!'
    #GPIO.cleanup()
    sys.exit(0)
    #MPCClient.command_queue.join()
# Connect singal_handler callback to sigint
signal.signal(signal.SIGINT, signal_handler)



class RadioFrame(frame.Frame):
    """
    Frame for internet radio
    """
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        self.widget_title_line = self.BuildWidget(widget.ScrollingLine, row=0, col=0)
        #self.widget_title_line.set_contents("InternetRadio")

        self.widget_track_line = self.BuildWidget(widget.LineWidget, row=1, col=2)
        #line2.set_contents("jawoi")

class SwitchToUPnPFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("Starte UPnP...")


class SwitchToRadioFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("Starte Radio...")


class UPnPFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("UPnP Modus")


class RadioApp(LcdUi):
    """

    """
    def __init__(self):
        device = MockCharacterDisplay(16, 2)
        LcdUi.__init__(self, device)
        self.initialize()

    def initialize(self):
        """
        Initializes all frames and sets up the events
        """
        self.radio_frame = RadioFrame(self)
        self.radio_frame.KeyDown += self.radio_keydown
        self._radio = InternetRadio(self.radio_frame)

        self.switch_to_radio_frame = SwitchToRadioFrame(self)
        self.switch_to_upnp_frame = SwitchToUPnPFrame(self)

        self.upnp_frame = UPnPFrame(self)
        self.upnp_frame.KeyDown += self.upnp_keydown

        self.radio_frame.Show()

    def switch_to_upnp(self):
        """
        Switches from intermission screen to upnp
        """
        self._radio.stop()
        self.switch_to_upnp_frame.Hide()
        self.upnp_frame.Show()

    def switch_to_radio(self):
        """
        Switches from intermission screen to radio
        """
        self.switch_to_radio_frame.Hide()
        self.radio_frame.Show()
        self._radio.start()

    def radio_keydown(self, key):
        """
        Handle keydown events that occur on the radio frame
        """
        if key == LcdUi.UIK_BUTTON:
            self.radio_frame.Hide()
            self.switch_to_upnp_frame.Show()
            t = Timer(1.5, self.switch_to_upnp)
            t.start()
        if key == LcdUi.UIK_NEXT:
            self._radio.next()
        if key == LcdUi.UIK_PREVIOUS:
            self._radio.previous()

    def upnp_keydown(self, key):
        """
        Handle keydown events that occur on the upnp frame
        """
        if key == LcdUi.UIK_BUTTON:
            self.upnp_frame.Hide()
            self.switch_to_radio_frame.Show()
            t = Timer(1.5, self.switch_to_radio)
            t.start()


def main():
    app = RadioApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
