'''
Base class for all game objects and helper methods to create them
'''
# pylint: disable=R0913

import struct

import moderngl
import pymunk


def create_box(x_pos, y_pos, width, height, mass, friction):
    '''
    Create a non-static box
    '''
    moment = pymunk.moment_for_box(mass, (width, height))
    body = pymunk.Body(mass, moment)
    body.position = pymunk.Vec2d(x_pos, y_pos)
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = friction
    return shape


def create_circle(x_pos, y_pos, radius, mass, friction):
    '''
    Create a non-static circle
    '''
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x_pos, y_pos)
    shape = pymunk.Circle(body, radius)
    shape.friction = friction
    return shape


class Entity:
    '''
    Represents any objects drawn on screen that's
    not the player or enemies (those are actors)
    '''
    # pylint: disable=R0902

    def __init__(self, x_pos, y_pos, width, height, shape, texture, static=False):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._width = width
        self._height = height

        # The pymunk shape
        self._shape = shape

        # The texture for the object
        self._texture = texture

        # If True, this item cannot be moved and has no physics applied
        self.static = static

        # Whether or not this entity can be collected
        # Set by subclass
        self._collectable = False

        # The value of the item if collected
        # Set by subclass. Can be callable or number
        self._value = None

        # Whether or not the entity can be broken
        self.breakable = False

        # An optional collectable entity that this object contains
        # Will appear when broken if it's breakable
        self.contains = None

    @property
    def x_pos(self):
        '''
        The current X position of the entity
        '''
        return self._shape.body.position.x

    @property
    def y_pos(self):
        '''
        The current Y position of the entity
        '''
        return self._shape.body.position.y

    @property
    def angle(self):
        '''
        Get the angle of the object
        '''
        return self._shape.body.angle

    @property
    def width(self):
        '''
        Get the width of the object
        '''
        return self._width

    @property
    def height(self):
        '''
        Get the height of the object
        '''
        return self._height

    @property
    def value(self):
        '''
        Get the value of the item
        '''
        if callable(self._value):
            return self._value()  # pylint: disable=E1102
        return self._value

    def apply_force(self, x_force, y_force, local_x=0, local_y=0):
        '''
        Apply a force to the body
        '''
        self._shape.body.apply_impulse_at_local_point((x_force, y_force), (local_x, local_y))

    def add_to_space(self, space):
        '''
        Add this object to the pymunk space
        '''
        space.add(self._shape.body, self._shape)

    def is_collectable(self):
        '''
        Return whether or not the item is collectable
        '''
        return self._collectable

    def to_bytes(self):
        '''
        Convert the object raw bytes to be written to the OpenGL buffer
        '''
        return struct.pack(
            '3f2f4f', self.x_pos, self.y_pos,
            self.angle, (self.width / 2), (self.height / 2),
            1, 1, 1, 0
        )

    def get_texture_location(self):
        '''
        Return the location attribute of the texture
        '''
        return self._texture.location


class EntityManager:
    '''
    Has list of all entities for a level (static and dynamic) and handles rendering
    them efficiently
    '''

    def __init__(self, space, frame_buffer, vertex_array, program):
        # The pymunk space
        self.space = space

        # The modern GL frame buffer
        self.frame_buffer = frame_buffer

        # The modern GL vertex array
        self.vertex_array = vertex_array

        # The modern GL shader program
        self.program = program

        self._entities = {}

    def add(self, entity):
        '''
        Add the entity to the entity tracker
        and the pymunk physics space
        '''
        ent_type = entity.__class__.__name__

        if ent_type not in self._entities:
            self._entities[ent_type] = []

        self._entities[ent_type].append(entity)
        entity.add_to_space(self.space)

    def draw(self):
        '''
        Draw the entities on the screen
        '''
        for _, entities in self._entities.items():
            # Entities are grouped by type and drawn all at once (per type)
            self.frame_buffer.write(b''.join(ent.to_bytes() for ent in entities))
            self.program["Texture"].value = entities[0].get_texture_location()
            self.vertex_array.render(moderngl.TRIANGLE_STRIP, instances=len(entities))
            self.frame_buffer.orphan()
