import RPi.GPIO as GPIO
import time

a_pin = 3
b_pin = 4

def main():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	while 1:
		a = GPIO.input(a_pin)
	        b = GPIO.input(b_pin)

	        print('%s %s' % (a,b))
		
	#	time.sleep(0.1)


if __name__ == '__main__':
        main()

