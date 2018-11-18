'''
Main game engine
'''

import os
import struct
import logging

import moderngl
import pymunk
from pymunk import Vec2d
from PIL import Image

from jackit2.core import VERTEX_SHADER, FRAGMENT_SHADER
from deploy import SITE_DEPLOYMENT

LOGGER = logging.getLogger(__name__)


class EngineSingleton:
    '''
    Main game engine.
    '''

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
        #: Get the game's config
        self.config = SITE_DEPLOYMENT.config
        #: Total points
        self.total_points = 0
        #: Number of deaths (factors into final score)
        self.deaths = 0

    def setup(self):
        '''
        Called to setup the OpenGL context
        '''
        self.ctx = moderngl.create_context()
        self.program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        sprites_path = os.path.join(SITE_DEPLOYMENT.resource_path, 'sprites')
        crate = Image.open(os.path.join(sprites_path, "crate.png")).convert('RGBA')
        self.tex1 = self.ctx.texture(crate.size, 4, crate.tobytes())
        self.tex1.use(0)

        ball = Image.open(os.path.join(sprites_path, "ball.png")).convert('RGBA')
        self.tex2 = self.ctx.texture(ball.size, 4, ball.tobytes())
        self.tex2.use(1)

        vbo1 = self.ctx.buffer(
            struct.pack(
                '16f',
                -1.0, -1.0, 0.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, -1.0, 1.0, 0.0,
                1.0, 1.0, 1.0, 1.0,
            )
        )

        self.vbo2 = self.ctx.buffer(reserve=(1024 * 1024))

        vao_content = [
            (vbo1, '2f 2f', 'in_vert', 'in_texture'),
            (self.vbo2, '3f 2f 4f /i', 'in_pos', 'in_size', 'in_tint'),
        ]

        self.vao = self.ctx.vertex_array(self.program, vao_content)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        shape = pymunk.Segment(self.space.static_body, (5, 100), (595, 100), 1.0)
        shape.friction = 1.0
        self.space.add(shape)

        x=Vec2d(-270, 7.5) + (300, 100)
        y=Vec2d(0, 0)
        deltaX=Vec2d(0.5625, 1.1) * 20
        deltaY=Vec2d(1.125, 0.0) * 20

        self.bodies = []
        self.balls = []

        for x in range(5):
            for y in range(10):
                size = 20
                mass = 10.0
                moment = pymunk.moment_for_box(mass, (size, size))
                body = pymunk.Body(mass, moment)
                body.position = Vec2d(300 + x * 50, 105 + y * (size + 0.1))
                shape = pymunk.Poly.create_box(body, (size, size))
                shape.friction = 0.3
                self.space.add(body, shape)
                self.bodies.append(body)

    def shoot(self):
        mass = 100
        r = 15
        moment = pymunk.moment_for_circle(mass, 0, r, (0,0))
        body = pymunk.Body(mass, moment)
        body.position = (0, 165)
        shape = pymunk.Circle(body, r, (0,0))
        shape.friction = 0.3
        self.space.add(body, shape)
        f = 50000
        body.apply_impulse_at_local_point((f,0), (0,0))
        self.balls.append(body)

    def update(self, viewport, elapsed):
        '''
        Updates all game components
        '''
        self.ctx.viewport = viewport
        self.ctx.clear(240, 240, 240)
        self.ctx.enable(moderngl.BLEND)

        for _ in range(10):
            self.space.step(0.001)

        self.program['Camera'].value = (200, 300, viewport[2] / 2, viewport[3] / 2)

        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 10, 10, 1, 1, 1, 0) for b in self.bodies))
        self.program['Texture'].value = 0
        self.vao.render(moderngl.TRIANGLE_STRIP, instances=len(self.bodies))

        self.vbo2.orphan()

        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 15, 15, 1, 1, 1, 0) for b in self.balls))
        self.program['Texture'].value = 1
        self.vao.render(moderngl.TRIANGLE_STRIP, instances=len(self.balls))

    def quit(self):
        '''
        Quits the game
        '''
        pass


GAME_ENGINE = EngineSingleton.instance()
