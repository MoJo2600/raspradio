import RPi.GPIO as GPIO
import time

class RotaryEncoder:
	def __init__(self, a_pin, b_pin, sw_pin):
		self.a_pin = a_pin
		self.b_pin = b_pin
		self.sw_pin = sw_pin
		self.rotary_step = 0

		GPIO.setmode(GPIO.BCM)

		GPIO.setup(self.a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.a_pin, GPIO.BOTH, callback=self._rotate_callback, bouncetime=10)
		GPIO.add_event_detect(self.sw_pin, GPIO.FALLING, callback=self._button_callback, bouncetime=300)

	def _button_callback(self, channel):
		print "button pressed"


	def _rotate_callback(self, channel):
		a = GPIO.input(self.a_pin)
		b = GPIO.input(self.b_pin)
		if a == b:
			self.rotary_step -= 1
		else:
		        self.rotary_step += 1

	def get_steps(self):
		return self.rotary_step
	

encoder = RotaryEncoder(4, 3, 2)
last_step = 0
while 1:
	rotary_step = encoder.get_steps()
	if last_step > rotary_step:		
		print(">")
		last_step = rotary_step
	elif last_step < rotary_step:
		print("<")
		last_step = rotary_step
	time.sleep(0.1)
