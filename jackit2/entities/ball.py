'''
A ball entity
'''

from jackit2.util import get_texture_loader
from jackit2.core.entity import Entity, create_circle


class Ball(Entity):
    '''
    A crate object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = get_texture_loader()
        super().__init__(
            x_pos, y_pos, width, height,
            create_circle(x_pos, y_pos, (width / 2), 100, 0.3),
            txs.get_texture_by_name("ball")
        )
