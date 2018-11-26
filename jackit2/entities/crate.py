'''
A crate entity
'''

from jackit2.util import get_texture_loader
from jackit2.core.entity import Entity, create_box


class Crate(Entity):
    '''
    A crate object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = get_texture_loader()
        super().__init__(
            x_pos, y_pos, width, height,
            create_box(x_pos, y_pos, width, height, 10, 0.3),
            txs.get_texture_by_name("crate")
        )
