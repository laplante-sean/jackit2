'''
A ball entity
'''

from jackit2.core.entity import Entity, create_circle
from jackit2.core.texture import TextureLoader


class Ball(Entity):
    '''
    A crate object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = TextureLoader.get()
        super().__init__(
            x_pos, y_pos, width, height,
            create_circle(x_pos, y_pos, (width / 2), 100, 0.3),
            txs.get_texture_by_name("ball")
        )
