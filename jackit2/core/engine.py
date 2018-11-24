'''
Main game engine
'''

import struct
import logging

import moderngl
import pymunk

from jackit2.core import VERTEX_SHADER, FRAGMENT_SHADER
from jackit2.core.texture import TextureLoader
from jackit2.core.camera import Camera, complex_camera
from jackit2.core.loader import LevelLoader
from jackit2.core.entity import EntityManager
from jackit2.core.audio import GameMusic

LOGGER = logging.getLogger(__name__)


class SetupFailed(Exception):
    '''
    Exception thrown if setup fails
    '''
    pass


class EngineSingleton:
    '''
    Main game engine.
    '''
    # pylint: disable=R0902

    _instance = None

    @classmethod
    def instance(cls):
        '''
        Get instance of EngineSingleton
        '''
        if cls._instance is None:
            cls._instance = EngineSingleton()
            return cls._instance
        return cls._instance

    def __init__(self):
        #: The game context
        self.ctx = None
        #: Vertex and fragment shader programs
        self.program = None
        #: Pymunk simulation space
        self.space = None
        #: The amount to step the physics engine on each frame
        self.physics_step = 0
        #: Loads the available game sounds
        self.sounds = None
        #: Load the game's music
        self.music = None
        #: Qt Main Windows set in setup()
        self.main_window = None
        #: Total points
        self.total_points = 0
        #: Number of deaths (factors into final score)
        self.deaths = 0
        #: Window width (populated in setup())
        self.width = 0
        #: Window height (populated in setup())
        self.height = 0
        #: The camera position
        self.camera = None
        #: The mouse position
        self.mouse_pos = None
        #: Aspect ratio for the resolution
        self.aspect_ratio = None
        #: Level loader
        self.levels = LevelLoader.get()
        #: Loads all textures
        self.textures = TextureLoader.get()
        #: The entity manager. Has all entities to be rendered. Setup in setup()
        self.entity_mgr = None
        #: The player
        self.player = None
        #: The frame buffer
        self.frame_buffer = None
        #: The vertex array
        self.vertex_array = None

    def setup(self, main_window):
        '''
        Called to setup the OpenGL context
        '''
        if not self.levels:
            raise SetupFailed("No levels could be loaded")

        self.width = main_window.width()
        self.height = main_window.height()
        self.main_window = main_window
        self.physics_step = 1.0 / self.main_window.framerate

        # Initialize modern GL context
        self.ctx = moderngl.create_context(require=430)
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.camera = Camera((self.width, self.height), complex_camera)
        self.program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        # Initialize physics
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        vbo = self.ctx.buffer(
            struct.pack(
                '16f',
                -1.0, -1.0, 0.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, -1.0, 1.0, 0.0,
                1.0, 1.0, 1.0, 1.0,
            )
        )

        self.frame_buffer = self.ctx.buffer(reserve=(self.width * self.height))

        varray_content = [
            (vbo, '2f 2f', 'in_vert', 'in_texture'),
            (self.frame_buffer, '3f 2f 4f /i', 'in_pos', 'in_size', 'in_tint'),
        ]

        self.vertex_array = self.ctx.vertex_array(self.program, varray_content)

        # Create the entity manager to draw and update all objects
        self.entity_mgr = EntityManager(self.space, self.frame_buffer, self.vertex_array, self.program)

        # Load textures
        self.textures.load(self.ctx)

        # Load the level
        lvl_width, lvl_height, self.player = self.levels[0].load(self.entity_mgr)

        # Update the camera
        self.camera.load_level((lvl_width, lvl_height))

        # Init the sound
        self.music = GameMusic()

        # Decides whether the sound is on by default or not
        self.music.play_game_music()

    def key_press(self, key):
        '''
        Key press event
        '''
        if key in ("w", " "):
            self.jump()
        if key == "d":
            self.right()
        if key == "a":
            self.left()
        if key == "m":
            self.music.toggle_game_music()

    def key_release(self, key):
        '''
        key release event
        '''
        pass

    def right(self):
        '''
        Move right
        '''
        if not self.player:
            return

        self.player.apply_world_force(80000, 0)

    def jump(self):
        '''
        Jump the player
        '''
        if not self.player:
            return

        self.player.apply_world_force(0, 80000)

    def left(self):
        '''
        Move left
        '''
        if not self.player:
            return

        self.player.apply_world_force(-80000, 0)

    def mouse_press(self, x_pos, y_pos):
        '''
        Called when the mouse is pressed
        '''
        self.mouse_pos = (x_pos, y_pos)

    def mouse_release(self, _x_pos, _y_pos):
        '''
        Called when the mouse is release
        '''
        self.mouse_pos = None

    def mouse_move(self, x_pos, y_pos):
        '''
        Called with the mouse position when it moves (only if a button is being held)
        '''
        if not self.mouse_pos:
            return

        # Calculate the amount the mouse has moved
        x_diff = self.mouse_pos[0] - x_pos
        y_diff = y_pos - self.mouse_pos[1]

        # Move the camera
        self.camera.move(x_diff, y_diff)

        self.mouse_pos = (x_pos, y_pos)  # Update the mouses position

    def mouse_wheel(self, delta):
        '''
        Called when the mouse wheel is spun. Positive number is wheel rotating away from user. Negative
        is when the wheel is rotated towards the user.
        '''
        self.camera.zoom(delta)

    def update(self):
        '''
        Updates all game components
        '''
        # Clear the screen
        self.ctx.clear(240, 240, 240)
        self.ctx.enable(moderngl.BLEND)

        # Step the physics engine a constant amount. We're banking on the
        # framerate being consistent. If the framerate is lower than in the
        # settings it should be adjusted to compensate for slower hardware
        self.space.step(self.physics_step)

        # Update the camera to follow the player
        if not self.mouse_pos:
            self.camera.update(self.player)

        # Display the camera
        self.camera.draw(self.program)

        # Draw all entities
        self.entity_mgr.draw()

    def quit(self):
        '''
        Quits the game
        '''
        pass


GAME_ENGINE = EngineSingleton.instance()
