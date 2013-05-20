import datetime


class Widget:
    def __init__(self, frame):
        self._frame = frame

    def Paint(self):
        return ''

    def Hide(self):
        """
        Calld when the widget is going to be hidden
        """
        pass

    def Show(self):
        """
        Called when the widget is going to be shown
        """
        pass

class ScrollingLine(Widget):
    def __init__(self, frame, contents='', speed=5):
        Widget.__init__(self, frame)
        self._contents = contents
        self.speed = speed
        #self._current_index = 0
        self._start_delay = 2  # 2 seconds delay before we start to scroll

        #self._last_repaint = datetime.datetime.now()

    def Show(self):
        """
        Reset everything to inital values
        """
        self._last_repaint = datetime.datetime.now()
        self._current_index = 0

    def Paint(self):
        cols = self._frame.cols()

        now = datetime.datetime.now()
        activity_delta = now - self._last_repaint
        if activity_delta.seconds < self._start_delay:
            return self._contents[:cols]

        # do not scroll if text fits in display
        if len(self._contents) < cols:
            return self._contents

        # reset current indes to start over again
        if self._current_index > len(self._contents):
            self._current_index = 0

        # calculate left and right part of string from current index position
        offset = self._current_index+cols
        if offset < len(self._contents):
            result = self._contents[self._current_index:offset]
        else:
            left_part = self._contents[self._current_index:]
            right_part = self._contents[:self._current_index]
            result = left_part + right_part

        self._current_index += 1
        return result[:cols]

    def set_contents(self, s):
        if len(s) > self._frame.cols():
            s += " --- "  # scroll divider
        self._contents = s

    def contents(self):
        return self._contents


class LineWidget(Widget):
    def __init__(self, frame, contents='', prefix='', postfix=''):
        Widget.__init__(self, frame)
        self._contents = contents
        self._prefix = prefix
        self._postfix = postfix
        self._wait_cursor = ['/', '-', '\\', '|']
        self._cursorstate = 0

    def Paint(self):
        if self._cursorstate > len(self._wait_cursor)-1:
            self._cursorstate = 0
#        self._postfix = self._wait_cursor[self._cursorstate]
        self._cursorstate += 1

        cols = self._frame.cols()
        outer_len = len(self._prefix) + len(self._postfix)
        inner_len = cols - outer_len
        contents = self._contents[:inner_len]
        contents += ' ' * (inner_len - len(contents))
        result = self._prefix + contents + self._postfix
        return result[:cols]

    def set_contents(self, s):
        self._contents = s

    def contents(self): return self._contents

    def set_prefix(self, s):
        self._prefix = s

    def prefix(self): return self._prefix

    def set_postfix(self, s):
        self._postfix = s

    def postfix(self): return self._postfix

