'''
Base class for levels
'''


class Level:
    '''
    Base class for a level
    '''

    def __init__(self, level_num, name="", description=""):
        self.level_num = level_num
        self.name = name
        self.description = description
