import signal
from lcd.devices.Generic import MockCharacterDisplay
from lcd.ui import ui
from lcd.ui import frame
from lcd.ui import widget
from lcd.ui.ui import LcdUi

#def signal_handler(signal, frame):
#    """
#	clean up before closing application
#	"""
# Connect singal_handler callback
#signal.signal(signal.SIGINT, signal_handler)


class FirstFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("FirstFrame")

        line1 = self.BuildWidget(widget.LineWidget, row=1, col=2)
        line1.set_contents("jawoi")


class SecondFrame(frame.Frame):
    def __init__(self, ui):
        frame.Frame.__init__(self, ui)

        line1 = self.BuildWidget(widget.LineWidget, row=0, col=0)
        line1.set_contents("Seconde Frame")

        line1 = self.BuildWidget(widget.LineWidget, row=1, col=2)
        line1.set_contents("frale")

class SampleApp(LcdUi):
    def __init__(self, parent):
        device = MockCharacterDisplay(16, 2)
        LcdUi.__init__(self, device)
        self.initialize()

    def initialize(self):
        f1 = FirstFrame(self)
        f2 = SecondFrame(self)
        #f = self.FrameFactory(frame.Frame)
        self.PushFrame(f1)

def main():
    app = SampleApp(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
