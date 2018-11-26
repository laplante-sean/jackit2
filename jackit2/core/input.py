'''
User input classes/methods
'''

from enum import Enum

from jackit2.util import get_game_engine


class InputEventType(Enum):
    '''
    Input event types
    '''
    KEY_PRESS = 0
    KEY_RELEASE = 1
    MOUSE_PRESS = 2
    MOUSE_RELEASE = 3
    MOUSE_MOVE = 4
    MOUSE_WHEEL = 5


def register_event_handler(handler, event_type):
    '''
    Register an input event handler with the game engine
    '''
    game_engine = get_game_engine()
    game_engine.register_event_handler(handler, event_type)
