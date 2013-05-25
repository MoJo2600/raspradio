import array
from common import Event


class Frame(object):
    """
    Represents a UI frame
    """
    def __init__(self, ui, *args, **kwargs):
        self._ui = ui
        self._screen_buffer = ScreenBuffer(self.rows(), self.cols())
        self._widgets = {}
        self._position = {}
        self._span = {}

        self.KeyDown = Event()

    def rows(self):
        """Returns the number of rows in the frame."""
        return self._ui.rows()

    def cols(self):
        """Returns the number of columns in the frame."""
        return self._ui.cols()

    def AddWidget(self, widget_obj, name, row=0, col=0, span=None):
        """Adds a widget to the current frame.

        Args:
          widget_obj: the widget to be added
          name: the name of the widget
          row: the row position of the widget
          col: the column position of the widget
          span: the character mask for the widget (or None if no mask)
        """
        self._widgets[name] = widget_obj
        self._position[name] = (row, col)
        self._span[name] = span or max(0, self.cols() - col)

    def BuildWidget(self, widget_cls, name=None, row=0, col=0, span=None, **kwargs):
        widget_obj = widget_cls(self, **kwargs)
        if name is None:
            name = widget_obj
        self.AddWidget(widget_obj, name, row, col, span)
        return widget_obj

    def Paint(self):
        for name, w in self._widgets.iteritems():
            outstr = w.Paint()
            row, col = self._position[name]
            span = self._span[name]
            self._screen_buffer.Write(array.array('c', outstr), row, col, span)
        return self._screen_buffer

    def Show(self):
        """
        Displays the frame
        """
        for widget in self._widgets:
            widget.Show()
        self._ui.PushFrame(self)

    def Hide(self):
        """
        Hides the frame
        """
        for widget in self._widgets:
            widget.Hide()
        self._ui.PopFrame()

    def clear(self):
        """
        Clears the Frame Contents
        """
        self._ui.clear()

class ScreenBuffer:
    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols
        self._array = array.array('c', [' '] * (rows * cols))

    def array(self):
        return self._array

    def _AllocNewArray(self):
        return array.array('c', [' '] * (self._rows * self._cols))

    def _GetOffset(self, row, col):
        return row * self._cols + col

    def Clear(self):
        self._array = self._AllocNewArray()

    def Write(self, data, row, col, span):
        """ replace data at row, col in this matrix """
        assert row in range(self._rows)
        assert col in range(self._cols)

        start = self._GetOffset(row, col)
        datalen = min(len(data), span)
        end = start + datalen
        self._array[start:end] = data[:datalen]

    def __str__(self):
        return self._array.tostring()
