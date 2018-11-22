'''
Main game engine
'''

import struct
import logging

import moderngl
import pymunk
from pymunk import Vec2d

from jackit2.core import VERTEX_SHADER, FRAGMENT_SHADER
from jackit2.core.texture import TextureLoader
from jackit2.core.camera import Camera, simple_camera

LOGGER = logging.getLogger(__name__)


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
        #: Loads all textures
        self.textures = TextureLoader()
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

    def translate_x(self, x_pos):
        '''
        Get the x coordinate
        '''
        return x_pos - (self.width // 2)  # Floor division

    def translate_y(self, y_pos):
        '''
        Get the y coordinate
        '''
        return (self.height // 2) - y_pos  # Floor division

    def pos(self, x_pos, y_pos):
        '''
        Given an x and y where (0, 0) is being treated as the
        top left corner of the screen, return a tuple of the
        (x, y) position to be used with pymunk and modernGL which
        has (0, 0) in the middle of the screen.
        '''
        return (self.translate_x(x_pos), self.translate_y(y_pos))

    def setup(self, main_window):
        '''
        Called to setup the OpenGL context
        '''
        self.width = main_window.width()
        self.height = main_window.height()
        self.main_window = main_window
        self.physics_step = 1.0 / self.main_window.framerate

        # Initialize modern GL context
        self.ctx = moderngl.create_context(require=430)
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.camera = Camera((self.width, self.height), simple_camera)
        self.program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        # Initialize physics
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        # Load textures
        self.textures.load(self.ctx)

        vbo1 = self.ctx.buffer(
            struct.pack(
                '16f',
                -1.0, -1.0, 0.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, -1.0, 1.0, 0.0,
                1.0, 1.0, 1.0, 1.0,
            )
        )

        self.vbo2 = self.ctx.buffer(reserve=(self.width * self.height))

        vao_content = [
            (vbo1, '2f 2f', 'in_vert', 'in_texture'),
            (self.vbo2, '3f 2f 4f /i', 'in_pos', 'in_size', 'in_tint'),
        ]

        self.vao = self.ctx.vertex_array(self.program, vao_content)

        shape = pymunk.Segment(
            self.space.static_body,
            self.pos(0, self.height),
            self.pos(self.width, self.height),
            10
        )

        shape.friction = 1.0
        shape.elasticity = 0.9
        self.space.add(shape)

        x = Vec2d(-270, 7.5) + (300, 100)
        y = Vec2d(0, 0)

        self.floor = shape
        self.bodies = []
        self.balls = []

        for x in range(5):
            for y in range(10):
                size = 64
                mass = 10.0
                moment = pymunk.moment_for_box(mass, (size, size))
                body = pymunk.Body(mass, moment)
                body.position = Vec2d(300 + x * 100, 105 + y * (size + 0.1))
                shape = pymunk.Poly.create_box(body, (size, size))
                shape.friction = 0.3
                self.space.add(body, shape)
                self.bodies.append(body)

    def shoot(self):
        mass = 100
        r = 32
        moment = pymunk.moment_for_circle(mass, 0, r, (0, 0))
        body = pymunk.Body(mass, moment)
        body.position = self.pos(0, 0)
        shape = pymunk.Circle(body, r, (0, 0))
        shape.friction = 0.3
        self.space.add(body, shape)
        f = 80000
        body.apply_impulse_at_local_point((f, 0), (0, 0))
        self.balls.append(body)
        #self.sounds.play("test")  # Play the test sound

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

        # Update the camera
        if self.balls:
            self.camera.update((self.balls[0].position.x, self.balls[0].position.y, 32, 32))

        # Draw on the screen
        self.program['Camera'].value = self.camera.get()
        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 32, 32, 1, 1, 1, 0) for b in self.bodies))
        self.program['Texture'].value = self.textures.get("crate").location
        self.vao.render(moderngl.TRIANGLE_STRIP, instances=len(self.bodies))

        self.vbo2.orphan()
        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 32, 32, 1, 1, 1, 0) for b in self.balls))
        self.program['Texture'].value = self.textures.get("ball").location
        self.vao.render(moderngl.TRIANGLE_STRIP, instances=len(self.balls))

    def quit(self):
        '''
        Quits the game
        '''
        pass


GAME_ENGINE = EngineSingleton.instance()
