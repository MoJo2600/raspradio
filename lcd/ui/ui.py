import Queue
import threading
import time
import datetime


class LcdUi(object):
    """
    UI framework for lcd displays
    """
    UIK_BUTTON = 0x00
    UIK_PREVIOUS = 0x01
    UIK_NEXT = 0x02

    def __init__(self, lcd, max_idle=60):
        super(LcdUi, self).__init__()
        self._lcd = lcd
        self._frame_stack = []
        self._last_paint = None
        self._quit = threading.Event()
        self._key_events = Queue.Queue()
        self.lock = threading.Lock()
        self._last_repaint = datetime.datetime.now()
        self._max_fps = 1000000 / 15  # max 15 fps

    def clear(self):
        """
        Clears the screen
        """
        self._lcd.ClearScreen()

    def Quit(self):
        with self.lock:
            self._quit.set()
            self._quit.clear()

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
        now = datetime.datetime.now()
        activity_delta = now - self._last_repaint
        if activity_delta.microseconds < self._max_fps:
            return

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

        self._last_repaint = datetime.datetime.now()

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

        # starting ui in an own thread
        uithread = threading.Thread(target=self._ui_loop)
        uithread.daemon = True
        uithread.start()

        # input thread
        command = None
        while command != 'x':
            try:
                command = raw_input("Commands (n)ext, (p)previous, (b)utton, e(x)it")
                if command == 'x':
                    self._quit.set()
                if command == 'n':
                    self._key_events.put(LcdUi.UIK_NEXT)
                if command == 'p':
                    self._key_events.put(LcdUi.UIK_PREVIOUS)
                if command == 'b':
                    self._key_events.put(LcdUi.UIK_BUTTON)
            except (KeyboardInterrupt, IOError, EOFError):
                self._quit.set()
                break

    def _ui_loop(self):
        """
        UI loop that refreshes the contents of the screen
        """
        self._lcd.ClearScreen()
        self._lcd.BacklightEnable(True)
        while not self._quit.isSet():
            self._step_loop()
            time.sleep(0.1)

    def _step_loop(self):
        """
        Execution routine of the ui_loop
        """
        # handle key inputs if needed
        self._HandleKeyEvents()

        # repaint as needed
        self._DoRepaint()

    def _HandleKeyEvents(self):
        """
        Handles the key events that have been stored in the _key_events Queue
        """
        while True:
            try:
                event = self._key_events.get_nowait()
            except Queue.Empty:
                return

            current_frame = self.CurrentFrame()
            if current_frame:
                current_frame.KeyDown(event)

