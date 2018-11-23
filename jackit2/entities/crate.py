'''
A crate entity
'''

from jackit2.core.entity import Entity, create_box
from jackit2.core.texture import TextureLoader


class Crate(Entity):
    '''
    A crate object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = TextureLoader.get()
        super().__init__(
            x_pos, y_pos, width, height,
            create_box(x_pos, y_pos, width, height, 10, 0.3),
            txs.get_texture_by_name("crate")
        )
