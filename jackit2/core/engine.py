'''
Main game engine
'''

import struct
import logging

import moderngl
import pymunk

from jackit2.core import VERTEX_SHADER, FRAGMENT_SHADER
from jackit2.util import get_config, get_texture_loader, get_level_loader
from jackit2.core.camera import Camera, complex_camera
from jackit2.core.entity import EntityManager
from jackit2.core.audio import GameAudio
from jackit2.core.input import InputEventType

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
        #: The main config
        self.config = get_config()
        #: Level loader
        self.levels = get_level_loader()
        #: Loads all textures
        self.textures = get_texture_loader()
        #: Deals with game audio
        self.audio = GameAudio()
        #: List of registered input handling functions
        self.input_handlers = {}
        #: True if dev mode is enabled
        self.dev_mode = self.config.is_development_mode()

        #: The game context
        self.ctx = None
        #: Vertex and fragment shader programs
        self.program = None
        #: Pymunk simulation space
        self.space = None
        #: The camera position
        self.camera = None
        #: The mouse position
        self.mouse_pos = None
        #: The entity manager. Has all entities to be rendered. Initialized in setup()
        self.entity_mgr = None
        #: The player
        self.player = None
        #: The frame buffer
        self.frame_buffer = None
        #: The vertex array
        self.vertex_array = None

        #: Total points
        self.total_points = 0
        #: Number of deaths (factors into final score)
        self.deaths = 0
        #: Window width (populated in setup())
        self.width = 0
        #: Window height (populated in setup())
        self.height = 0
        #: The amount to step the physics engine on each frame
        self.physics_step = 0

    def setup(self, width, height, framerate):
        '''
        Called to setup the OpenGL context
        '''
        if not self.levels:
            raise SetupFailed("No levels could be loaded")

        # Window width and height
        self.width = width
        self.height = height

        # How much to step the physics on each frame
        self.physics_step = 1.0 / framerate

        # Initialize modern GL context, camera, and shaders
        self.ctx = moderngl.create_context(require=430)
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.camera = Camera((self.width, self.height), complex_camera, initial_scale=self.config.high_dpi_scaling)
        self.program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        # Initialize physics
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        vbo = self.ctx.buffer(struct.pack(
            '16f', -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ))

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
        self.audio = GameAudio()

        # Decides whether the sound is on by default or not
        if self.config.music_enabled:
            self.audio.play_game_music()

    def update(self):
        '''
        Updates all game components
        '''
        # Clear the screen
        self.ctx.clear(0, 0, 0)
        self.ctx.enable(moderngl.BLEND)

        # Step the physics engine a constant amount. We're banking on the
        # framerate being consistent. If the framerate is lower than in the
        # settings it should be adjusted to compensate for slower hardware
        self.space.step(self.physics_step)

        if self.mouse_pos is None:
            # Update the camera to follow the player
            self.camera.update(self.player)

        # Display the camera
        self.camera.draw(self.program)

        # Draw all entities
        self.entity_mgr.draw()

    def handle_input_event(self, event, event_type):
        '''
        Handle an input event
        '''

        # First call the registered handlers
        for handler in self.input_handlers.get(event_type, []):
            if not handler(event):
                break  # If a handler returns false don't pass the event to any other handlers

        if self.dev_mode:
            # In dev mode we allow some additional controls
            # for level/camera exploring
            if event_type == InputEventType.MOUSE_PRESS:
                self.mouse_press(event.x(), event.y())
            elif event_type == InputEventType.MOUSE_RELEASE:
                self.mouse_release(event.x(), event.y())
            elif event_type == InputEventType.MOUSE_MOVE:
                self.mouse_move(event.x(), event.y())
            elif event_type == InputEventType.MOUSE_WHEEL:
                self.mouse_wheel(event.angleDelta().y())

    def register_event_handler(self, handler, event_type):
        '''
        Register an event handler
        '''
        if event_type not in self.input_handlers:
            self.input_handlers[event_type] = []
        self.input_handlers[event_type].append(handler)

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
        if self.mouse_pos is None:
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

    def quit(self):  # pylint: disable=R0201
        '''
        Quits the game
        '''
        LOGGER.debug("EngineSingleton.quit()")


GAME_ENGINE = EngineSingleton.instance()
