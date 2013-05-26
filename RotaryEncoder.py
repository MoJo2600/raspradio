import RPi.GPIO as GPIO
import threading
from common import Event

ROTARY_A_PIN = 0  # A pin of the rotary encoder
ROTARY_B_PIN = 0  # B pin of the rotary encoder
ROTARY_SWITCH_PIN = 0  # Switch pin of the rotary encoder
SET_COUNT = 0
ROTARY_EVENT = GPIO.RISING
BOUNCETIME = 30   # Bouncetime for the rotary encoder

CW = Event()
CCW = Event()
BUTTON = Event()

def rotate_callback(channel):
    """
    callback function for the input pin interrupt
    implemented according to the documentation:
    http://www.produktinfo.conrad.com/datenblaetter/700000-724999/705594-da-01-ml-Drehimpulsgeber_stehend_de_en.pdf
    had to place it in a global function, because i had AttributeErrors when
    implemented in a class
    TODO: lock necessary? hm...
    """
    global ROTARY_A_PIN
    global ROTARY_B_PIN
    global SET_COUNT
    global ROTARY_EVENT

    GPIO.remove_event_detect(channel)  # disconnect the interrupt
    a = GPIO.input(channel)
    b = GPIO.input(ROTARY_B_PIN)
    if a == b:
        SET_COUNT -= 1
        CW()
    else:
        SET_COUNT += 1
        CCW()
    # switch the interrupt from rising to falling edge and vice versa
    ROTARY_EVENT = GPIO.FALLING if ROTARY_EVENT == GPIO.RISING else GPIO.RISING
    GPIO.add_event_detect(channel, ROTARY_EVENT, callback=rotate_callback, bouncetime=BOUNCETIME)

def button_callback(channel):
    """
    callback function for the switch input pin interrupt
    """
    BUTTON()

class RotaryEncoder:
    """
    implementation for rotary encoder
    """
    def __init__(self, a_pin, b_pin, sw_pin):
        """
        Initializes the instance of RotaryEncoder
        :param a_pin: A pin of rotary encoder
        :param b_pin: B pin of rotary encoder
        :param sw_pin: Switch pin of rotary encoder
        """
        global ROTARY_A_PIN
        global ROTARY_B_PIN
        global ROTARY_SWITCH_PIN

        ROTARY_A_PIN = a_pin
        ROTARY_B_PIN = b_pin
        ROTARY_SWITCH_PIN = sw_pin

        self.lock = threading.Lock()
        self.sw_pin = sw_pin
        self.rotary_step = 0
        self._event = GPIO.RISING

        # Events for easy binding
        self.CW = CW
        self.CCW = CCW
        self.BUTTON = BUTTON

        # Setup all used ports
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ROTARY_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROTARY_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(ROTARY_A_PIN, ROTARY_EVENT, callback=rotate_callback, bouncetime=BOUNCETIME)
        GPIO.add_event_detect(ROTARY_SWITCH_PIN, GPIO.RISING, callback=button_callback, bouncetime=100)
