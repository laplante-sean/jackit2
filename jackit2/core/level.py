'''
Base class for levels
'''

from jackit2.core import BLOCK_HEIGHT, BLOCK_WIDTH
from jackit2.entities import Floor, Wall, Crate
from jackit2.actors.player import Player


class LevelGeneratorError(Exception):
    '''
    Error generating the level from the map provided
    '''
    pass


class LevelMap:
    '''
    Level map format characters
    '''
    # pylint: disable=R0903
    EXIT = "E"
    SPAWN = "S"
    FLOOR = "F"
    WALL = "W"
    CRATE = "C"


class Level:
    '''
    Base class for a level
    '''
    # pylint: disable=R0902,R0903

    def __init__(self, level_num, level_map, name="", description=""):
        self.level_num = level_num
        self.name = name
        self.description = description
        self.level_map = level_map

        #: Automatically populated with the level's pixel width and height
        #: Once it has been loaded
        self.width = 0
        self.height = 0

        #: (x, y) coordinates of the top left and bottom right corners of
        #: a rectangle that represents the "live-able" area of the level.
        #: anything outside this should be destroyed.
        self.death_zone = (0, 0, 0, 0)

        # Set when building the level to the object on the spawn point
        self.player = None

    def load(self, entity_mgr):
        '''
        Load the level
        '''
        # Build the level from the map
        self.width, self.height = self._build_level(entity_mgr)

        # Coordinates for  rectangle 50 pixels bigger on all sides than the level
        self.death_zone = (-50, -50, self.width + 50, self.height + 50)

        return self.width, self.height, self.player

    def _build_level(self, entity_mgr):
        '''
        Build the level from the map
        '''

        cur_x = cur_y = 0
        entity = None
        self.level_map.reverse()
        for row in self.level_map:
            for col in row:
                args = [cur_x, cur_y, BLOCK_WIDTH, BLOCK_HEIGHT]
                # sprite = None
                if col == LevelMap.FLOOR:
                    entity = Floor(*args)
                elif col == LevelMap.EXIT:
                    # sprite = self.create_exit_block(x, y)
                    pass
                elif col == LevelMap.SPAWN:
                    self.player = entity = Player(cur_x, cur_y)
                elif col == LevelMap.WALL:
                    entity = Wall(*args)
                elif col == LevelMap.CRATE:
                    entity = Crate(*args)
                elif col == ' ':
                    # Empty space is empty space
                    pass
                else:
                    raise LevelGeneratorError("Unknown block character '{}'".format(col))

                if entity:
                    entity_mgr.add(entity)
                    entity = None

                cur_x += BLOCK_WIDTH
            cur_y += BLOCK_HEIGHT
            cur_x = 0

        total_level_width = len(max(self.level_map, key=len)) * BLOCK_WIDTH
        total_level_height = len(self.level_map) * BLOCK_HEIGHT
        return total_level_width, total_level_height
