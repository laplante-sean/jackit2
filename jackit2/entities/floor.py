'''
A floor entity
'''

from jackit2.util import get_texture_loader
from jackit2.core.entity import Entity, create_static_box


class Floor(Entity):
    '''
    A floor object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = get_texture_loader()
        super().__init__(
            x_pos, y_pos, width, height,
            create_static_box(x_pos, y_pos, width, height, 0.5),
            txs.get_texture_by_name("floor")
        )
