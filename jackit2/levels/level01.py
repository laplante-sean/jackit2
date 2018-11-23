'''
Level 1
'''

from jackit2.core.level import Level


class Level01(Level):
    '''
    Basic training level
    '''
    # pylint: disable=R0903

    _map = [
        "WWWWWWWWWWWWWWWWWWWWWWW",
        "W                     W",
        "W                     W",
        "W                     E",
        "W                     E",
        "W          FFFFFFFFFFFWWWWWWWWWWWWWWWWWWWWWW",
        "W             C                            W",
        "WFFFFF        C                            W",
        "W     F       C                            W",
        "W      F      C              C             W",
        "W       FFF   C             CCC            W",
        "W           FFF            CCCCC           W",
        "W                FFF      CCCCCCC          W",
        "W               C        CCCCCCCCC         W",
        "W               CC      FFFFFFFFFFF        W",
        "W               CCC                        W",
        "W               CCCCCC                     W",
        "W            FFFFFFFFFFF                   W",
        "W                         CCCCCCCCCC       W",
        "W    S                    CCCCCCCCCC       W",
        "W                         CCCCCCCCCC       W",
        "W                         CCCCCCCCCC       W",
        "W                         CCCCCCCCCC       W",
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
    ]

    def __init__(self):
        super().__init__(1, self._map, "Basic", "Basic training level")


__Level__ = Level01  # pylint: disable=C0103
