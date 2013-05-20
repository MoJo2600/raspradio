#!/usr/bin/python
from threading import Timer
from lcd.devices.Generic import MockCharacterDisplay
from lcd.ui import frame
from lcd.ui import widget
from lcd.ui.ui import LcdUi


class FirstFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.ScrollingLine, row=0, col=0)
        line1.set_contents("Longtext will be scrolling - and scrolling - and scrolling")

        line1 = self.BuildWidget(widget.LineWidget, row=1, col=2)
        line1.set_contents("jawoi")

class IntermissionFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.ScrollingLine, row=0, col=0)
        line1.set_contents("Switching between Frames")

class SecondFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("Second Frame")

        line1 = self.BuildWidget(widget.LineWidget, row=1, col=2)
        line1.set_contents("frale")


class SampleApp(LcdUi):
    def __init__(self):
        device = MockCharacterDisplay(16, 2)
        LcdUi.__init__(self, device)
        self.initialize()

    def initialize(self):
        self.f1 = FirstFrame(self)
        self.f1.KeyDown += self.frame1_button_pressed

        self.intermission_frame = IntermissionFrame(self)

        self.f2 = SecondFrame(self)
        self.f2.KeyDown += self.frame2_button_pressed

        self.f1.Show()

    def switch_to_frame2(self):
        self.f1.Hide()
        self.f2.Show()

    def switch_to_frame1(self):
        self.f2.Hide()
        self.f1.Show()

    def frame1_button_pressed(self, key):
        print "frame1 keypress %s" % key
        if key == LcdUi.UIK_BUTTON:
            # switch frames to see if events are correct propagated
            self.f1.Hide()
            self.intermission_frame.Show()
            t = Timer(3.0, self.switch_to_frame2)
            t.start()

    def frame2_button_pressed(self, key):
        print "frame2 keypress %s" % key
        if key == LcdUi.UIK_BUTTON:
            # switch frames to see if events are correct propagated
            self.f2.Hide()
            self.intermission_frame.Show()
            t = Timer(3.0, self.switch_to_frame1)
            t.start()

def main():
    app = SampleApp()
    app.MainLoop()

if __name__ == '__main__':
    main()
