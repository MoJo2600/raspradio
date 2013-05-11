import RPi.GPIO as GPIO
import time
from RotaryEncoder import RotaryEncoder

#class RotaryEncoder:
#
#	def __init__(self):
#		self._a = 4
#		self._b = 3
#
#	def debounce(self):



encoder = RotaryEncoder(4, 3, 2)
encoder.setup()
last_step = 0
while 1:
	rotary_step = encoder.get_steps()
	if last_step > rotary_step:		
		print(">")
		last_step = rotary_step
	elif last_step < rotary_step:
		print("<")
		last_step = rotary_step
#	time.sleep(0.01)
