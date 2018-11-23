'''
Classes used to load textures
'''

import os
import logging

from PIL import Image

LOGGER = logging.getLogger(__name__)
G_TEX_LOCATION = 0


def get_next_location():
    '''
    Get the next valid location for a texture
    '''
    global G_TEX_LOCATION  # pylint: disable=W0603
    ret = G_TEX_LOCATION
    G_TEX_LOCATION += 1
    return ret


class Texture:
    '''
    Used to represent and load a texture from an image file
    '''

    def __init__(self, path, gl_ctx):
        #: Path to the texture file
        self.path = path
        #: ModernGL Context
        self.ctx = gl_ctx
        #: Loaded image
        self.image = Image.open(self.path).convert('RGBA')
        #: ModernGL texture. Image size, 4 components (e.g. RGBA), and the image bytes
        self.texture = self.ctx.texture(self.image.size, 4, self.image.tobytes())
        #: Unique location - Binding point for texture
        self.location = get_next_location()
        #: Set the texture's binding point
        self.texture.use(location=self.location)

    def get(self):
        '''
        Get the ModernGL texture
        '''
        return self.texture


class TextureLoader:
    '''
    Loads all textures
    '''

    _instance = None

    def __init__(self):
        self._textures = {}

    @classmethod
    def create(cls):
        '''
        Create an instance of the texture loader
        '''
        ldr = cls()
        TextureLoader._instance = ldr
        return ldr

    @classmethod
    def get(cls):
        '''
        Get or create an instance of the texture loader
        '''
        return cls._instance or cls.create()

    def get_texture_by_name(self, name):
        '''
        Get a texture by its name
        '''
        if name not in self._textures:
            raise KeyError("No texture found with name '{}'".format(name))
        return self._textures[name]

    def load(self, gl_ctx):
        '''
        Load all the textures
        '''
        from deploy import SITE_DEPLOYMENT

        for (dirpath, _, filenames) in os.walk(SITE_DEPLOYMENT.texture_path):
            for filename in filenames:
                if not filename.endswith(".png"):
                    LOGGER.warning("file '%s' in textures directory is not a texture", filename)
                    continue

                LOGGER.debug("loading texture: %s", filename)
                path = os.path.join(dirpath, filename)
                name = os.path.splitext(filename)[0]  # Grab the filename component w/o file ext.

                if name not in self._textures:
                    self._textures[name] = Texture(path, gl_ctx)
                else:
                    LOGGER.warning("texture with name '%s' has already been loaded.", name)
