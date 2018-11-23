'''
A floor entity
'''

from jackit2.core.entity import Entity, create_static_box
from jackit2.core.texture import TextureLoader


class Floor(Entity):
    '''
    A floor object
    '''

    def __init__(self, x_pos, y_pos, width, height):
        txs = TextureLoader.get()
        super().__init__(
            x_pos, y_pos, width, height,
            create_static_box(x_pos, y_pos, width, height, 0.5),
            txs.get_texture_by_name("crate")
        )
