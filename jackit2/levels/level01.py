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
        "W                                          W",
        "WFFFFF                                     W",
        "W     F                                    W",
        "W      F                                   W",
        "W       FFF                                W",
        "W           FFF                            W",
        "W                FFF                       W",
        "W                                          W",
        "W                       FFFFFFFFFFF        W",
        "W                                          W",
        "W                                          W",
        "W            FFFFFFFFFFF                   W",
        "W                                          W",
        "W    S                                     W",
        "W                         FFFFFFFFFF       W",
        "W                                          W",
        "W                                          W",
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
    ]

    def __init__(self):
        super().__init__(1, self._map, "Basic", "Basic training level")


__Level__ = Level01  # pylint: disable=C0103
