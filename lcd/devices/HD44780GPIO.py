# -*- coding: utf-8 -*-
import sys
import time
from lcd import common
from lcd.devices import Interfaces
import RPi.GPIO as GPIO


class HD44780GPIO(Interfaces.ICharacterDisplay):
    """
    Driver class for a HD44780 compatible display
    """
    DISPLAY_WIDTH = 16     # characters per row
    DISPLAY_LINE_1 = 0x80     # address of first row
    DISPLAY_LINE_2 = 0xC0     # address of second row
    DISPLAY_CHR = True
    DISPLAY_CMD = False
    E_PULSE = 0.00005
    E_DELAY = 0.00005
    STR_PAD = " " * 16

    SYMBOLS = {
        common.SYMBOL.ARROW_UP: '^',
        common.SYMBOL.ARROW_DOWN: 'v',
        common.SYMBOL.ARROW_LEFT: '<',
        common.SYMBOL.ARROW_RIGHT: '>',

        common.SYMBOL.TRIANGLE_UP: '^',
        common.SYMBOL.TRIANGLE_DOWN: 'v',
        common.SYMBOL.TRIANGLE_LEFT: '<',
        common.SYMBOL.TRIANGLE_RIGHT: '>',

        common.SYMBOL.PROGBAR_1: '#',
        common.SYMBOL.PROGBAR_2: '#',
        common.SYMBOL.PROGBAR_3: '#',
        common.SYMBOL.PROGBAR_4: '#',
        common.SYMBOL.PROGBAR_5: '#',

        common.SYMBOL.MENU_CURSOR: '*',
        common.SYMBOL.MENU_LIST_UP: '^',
        common.SYMBOL.MENU_LIST_DOWN: 'v',

        common.SYMBOL.FRAME_BACK: '<',
    }
    
    def __init__(self, pin_rs, pin_e, pin_data4, pin_data5, pin_data6, pin_data7, cols, rows):
        self._pin_rs = pin_rs
        self._pin_e = pin_e
        self._pin_data4 = pin_data4
        self._pin_data5 = pin_data5
        self._pin_data6 = pin_data6
        self._pin_data7 = pin_data7
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_e, GPIO.OUT)
        GPIO.setup(self._pin_rs, GPIO.OUT)
        GPIO.setup(self._pin_data4, GPIO.OUT)
        GPIO.setup(self._pin_data5, GPIO.OUT)
        GPIO.setup(self._pin_data6, GPIO.OUT)
        GPIO.setup(self._pin_data7, GPIO.OUT)

        self._rows = rows
        self._cols = cols
        self._contents = self._AllocContents()

        self.display_init()

    def display_init(self):
        self.lcd_byte(0x33,self.DISPLAY_CMD)
        self.lcd_byte(0x32,self.DISPLAY_CMD)
        self.lcd_byte(0x28,self.DISPLAY_CMD)
        self.lcd_byte(0x0C,self.DISPLAY_CMD)  
        self.lcd_byte(0x06,self.DISPLAY_CMD)
        self.lcd_byte(0x01,self.DISPLAY_CMD)      

    def lcd_clean_string(self, text):
        text = text.replace('ä', '\xE1')
        text = text.replace('ö', '\xEF')
        text = text.replace('ü', '\xF5')
        text = text.replace('Ä', '\xE1')
        text = text.replace('Ö', '\xEF')
        text = text.replace('Ü', '\xF5')
        text = text.replace('ß', '\xE2')
        return text

    def lcd_string(self, message):
        message = self.lcd_clean_string(message)
        message = message.ljust(self.DISPLAY_WIDTH," ")  
        for i in range(self.DISPLAY_WIDTH):
            self.lcd_byte(ord(message[i]),self.DISPLAY_CHR)

    def lcd_byte(self, bits, mode):
        GPIO.output(self._pin_rs, mode)
        GPIO.output(self._pin_data4, False)
        GPIO.output(self._pin_data5, False)
        GPIO.output(self._pin_data6, False)
        GPIO.output(self._pin_data7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self._pin_data4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self._pin_data5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self._pin_data6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self._pin_data7, True)
        time.sleep(self.E_DELAY)    
        GPIO.output(self._pin_e, True)  
        time.sleep(self.E_PULSE)
        GPIO.output(self._pin_e, False)  
        time.sleep(self.E_DELAY)      
        GPIO.output(self._pin_data4, False)
        GPIO.output(self._pin_data5, False)
        GPIO.output(self._pin_data6, False)
        GPIO.output(self._pin_data7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self._pin_data4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self._pin_data5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self._pin_data6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self._pin_data7, True)
        time.sleep(self.E_DELAY)    
        GPIO.output(self._pin_e, True)  
        time.sleep(self.E_PULSE)
        GPIO.output(self._pin_e, False)  
        time.sleep(self.E_DELAY)          

    def _AllocContents(self):
        return " " * (self._rows * self._cols)

    def ClearScreen(self):
        self.lcd_byte(0x01, self.DISPLAY_CMD)
#        self._contents = self._AllocContents()

    def BacklightEnable(self, enable):
        pass

    def GetSymbol(self, name, default=None):
        return self.SYMBOLS.get(name, default)

    def rows(self):
        return self._rows

    def cols(self):
        return self._cols

    def WriteScreen(self, buf):
        self._contents = buf
        for i in xrange(self._rows):
            rowtext = self._contents[i * self._cols:(i + 1) * self._cols].tostring()
            if i == 0:
                self.lcd_byte(HD44780GPIO.DISPLAY_LINE_1, HD44780GPIO.DISPLAY_CMD)
            if i == 1:
                self.lcd_byte(HD44780GPIO.DISPLAY_LINE_2, HD44780GPIO.DISPLAY_CMD)
            self.lcd_string(rowtext)
