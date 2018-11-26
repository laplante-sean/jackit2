'''
User controllable player
'''

from jackit2.core import BLOCK_HEIGHT, BLOCK_WIDTH
from jackit2.util import get_texture_loader
from jackit2.core.input import InputEventType, register_event_handler
from jackit2.core.entity import Entity, create_circle


class Player(Entity):
    '''
    User controlled player
    '''

    def __init__(self, x_pos, y_pos):
        txs = get_texture_loader()
        super().__init__(
            x_pos, y_pos, BLOCK_WIDTH, BLOCK_HEIGHT,
            create_circle(x_pos, y_pos, (BLOCK_WIDTH / 2), 100, 0.3),
            txs.get_texture_by_name("ball")
        )

        register_event_handler(self.key_press, InputEventType.KEY_PRESS)

    def key_press(self, event):
        '''
        Handle key press event
        '''
        if event.text() in (" ", "w"):
            self.apply_world_force(0, 900000)
            return False
        if event.text() == "d":
            self.apply_world_force(800000, 0)
            return False
        if event.text() == "a":
            self.apply_world_force(-800000, 0)
            return False

        return True
