"""https://code.google.com/p/pylcdui/"""
import util

SYMBOL = util.Enum(*(
    'ARROW_UP',
    'ARROW_DOWN',
    'ARROW_LEFT',
    'ARROW_RIGHT',

    'TRIANGLE_UP',
    'TRIANGLE_DOWN',
    'TRIANGLE_LEFT',
    'TRIANGLE_RIGHT',

    'PROGBAR_1',
    'PROGBAR_2',
    'PROGBAR_3',
    'PROGBAR_4',
    'PROGBAR_5',

    'MENU_CURSOR',
    'MENU_LIST_UP',
    'MENU_LIST_DOWN',

    'FRAME_BACK',
))
