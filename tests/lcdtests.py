#!/bin/python

device = HD44780GPIO(7, 8, 25, 24, 23, 18, 16, 2)
device.lcd_string("The Display", 
