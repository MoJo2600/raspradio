import threading
import time


class LcdUi:
    def __init__(self, lcd, max_idle=60):
        self._lcd = lcd
        self._frame_stack = []
        self._last_paint = None
        self._quit = threading.Event()

    def rows(self):
        return self._lcd.rows()

    def cols(self):
        return self._lcd.cols()

    def FrameFactory(self, frame_cls, **kwargs):
        return frame_cls(ui=self)

    def CurrentFrame(self):
        if len(self._frame_stack):
          return self._frame_stack[-1]
        else:
          return None

    def Repaint(self):
        """Redraw the screen with the current frame"""
        self._DoRepaint()

    def _DoRepaint(self):
        current_frame = self.CurrentFrame()
        current_buffer = None

        if current_frame is not None:
            current_buffer = current_frame.Paint().array()
            current_str = current_buffer.tostring()

        if current_str != self._last_paint:
            self._last_paint = current_str
            if current_buffer is None:
                self._lcd.ClearScreen()
            else:
                self._lcd.WriteScreen(current_buffer)

    def PushFrame(self, frame):
        """Add a frame to the top of the stack and set as current"""
        self._frame_stack.append(frame)

    def PopFrame(self):
        """Remote the topmost frame on the stack and set new current frame.

        If the stack is empty as a result of the pop, a psuedoframe consisting of
        the blank screen will be drawn. If the stack is already empty, an exception
        is raised.
        """
        if not self._frame_stack:
            return
        ret = self._frame_stack[-1]
        self._frame_stack = self._frame_stack[:-1]
        return ret

    def MainLoop(self):
        """
        runs the gui in a loop
        """
        self._lcd.ClearScreen()
        self._lcd.BacklightEnable(True)
        while not self._quit.isSet():
            self._step_loop()
            time.sleep(0.01)

    def _step_loop(self):
        # handle key inputs if needed
        #self._HandleKeyEvents()

        # repaint as needed
        self._DoRepaint()