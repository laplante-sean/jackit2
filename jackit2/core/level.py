'''
Base class for levels
'''

from jackit2.core import BLOCK_HEIGHT, BLOCK_WIDTH


class LevelGeneratorError(Exception):
    '''
    Error generating the level from the map provided
    '''
    pass


class LevelMap:
    '''
    Level map format characters
    '''
    EXIT = "E"
    SPAWN = "S"
    FLOOR = "F"
    WALL = "W"


class Level:
    '''
    Base class for a level
    '''

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

    def load(self):
        '''
        Load the level
        '''
        # Build the level from the map
        self.width, self.height = self._build_level()

        # Coordinates for  rectangle 50 pixels bigger on all sides than the level
        self.death_zone = (-50, -50, self.width + 50, self.height + 50)

        return self.width, self.height

    def _build_level(self):
        '''
        Build the level from the map
        '''

        cur_x = cur_y = 0
        for row in self.level_map:
            for col in row:
                # sprite = None
                if col == LevelMap.FLOOR:
                    # sprite = self.create_platform(x, y, platform_type="ground")
                    pass
                elif col == LevelMap.EXIT:
                    # sprite = self.create_exit_block(x, y)
                    pass
                elif col == LevelMap.SPAWN:
                    # self.player.spawn_point = (x, y)
                    pass
                elif col == LevelMap.WALL:
                    pass
                elif col == ' ':
                    # Empty space is empty space
                    pass
                else:
                    raise LevelGeneratorError("Unknown block character '{}'".format(col))

                cur_x += BLOCK_WIDTH
            cur_y += BLOCK_HEIGHT
            cur_x = 0

        total_level_width = len(max(self.level_map, key=len)) * BLOCK_WIDTH
        total_level_height = len(self.level_map) * BLOCK_HEIGHT
        return total_level_width, total_level_height
