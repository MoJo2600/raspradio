import RPi.GPIO as GPIO
import time

ROTARY_A_PIN = 0
ROTARY_B_PIN = 0
SET_COUNT = 0
ROTARY_EVENT = GPIO.RISING
BOUNCETIME = 30

def rotate_callback(channel):
	global ROTARY_A_PIN
	global ROTARY_B_PIN
	global SET_COUNT
	global ROTARY_EVENT

	GPIO.remove_event_detect(channel)
	a = GPIO.input(channel)
	b = GPIO.input(ROTARY_B_PIN)
	print ('%s %s' % (a, b))
	if a == b:
		SET_COUNT -= 1
	else:
	        SET_COUNT += 1
	if ROTARY_EVENT == GPIO.RISING:
		ROTARY_EVENT = GPIO.FALLING
	elif ROTARY_EVENT == GPIO.FALLING:
		ROTARY_EVENT = GPIO.RISING
	GPIO.add_event_detect(channel, ROTARY_EVENT, callback=rotate_callback, bouncetime=BOUNCETIME)


class RotaryEncoder:
	def __init__(self, a_pin, b_pin, sw_pin):
		global ROTARY_A_PIN
		global ROTARY_B_PIN
		ROTARY_A_PIN = a_pin
		ROTARY_B_PIN = b_pin
		self.sw_pin = sw_pin
		self.rotary_step = 0
		self._event = GPIO.RISING
		self._bouncetime = 30

		GPIO.setmode(GPIO.BCM)

		GPIO.setup(ROTARY_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(ROTARY_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#		GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(ROTARY_A_PIN, ROTARY_EVENT, callback=rotate_callback, bouncetime=self._bouncetime)
#		GPIO.add_event_detect(self.sw_pin, GPIO.FALLING, callback=self._button_callback, bouncetime=BOUNCETIME)

	def _button_callback(self, channel):
		print "button pressed"


	def get_steps(self):
		return SET_COUNT
	

#encoder = RotaryEncoder(4, 3, 2)
#last_step = 0
#while 1:
#	rotary_step = encoder.get_steps()
#	if last_step > rotary_step:		
#		print(">")
#		last_step = rotary_step
#	elif last_step < rotary_step:
#		print("<")
#		last_step = rotary_step
#	time.sleep(0.1)
