'''
Loads the levels dynamically
'''
import os
import logging
import types
from uuid import uuid4

from importlib.machinery import SourceFileLoader

LOGGER = logging.getLogger(__name__)


class LevelStub:
    '''
    Stub for a level class.
    '''

    def __init__(self, level_cls):
        self._level_cls = level_cls

    def load(self):
        '''
        Create an instance of the level
        '''
        return self._level_cls()

    def __call__(self):
        '''
        Trigger the level class instance to be created
        '''
        return self.load()


class LevelLoader:
    '''
    Searches for levels and loads them
    '''

    _instance = None

    def __init__(self):
        self.paths = []
        self._levels = []

    @classmethod
    def create(cls):
        '''
        Create an instance of the level loader
        '''
        ldr = cls()
        LevelLoader._instance = ldr
        return ldr

    @classmethod
    def get(cls):
        '''
        Get or create an instance of the level loader
        '''
        return cls._instance or cls.create()

    def __len__(self):
        '''
        Returns the number of levels
        '''
        return len(self._levels)

    def __iter__(self):
        '''
        Returns an iterator into the level list
        '''
        return iter(self._levels)

    def __getitem__(self, index):
        '''
        Returns level at index
        '''
        LOGGER.debug("__getitem__: %s", self._levels)
        return self._levels[index]()

    def get_by_num(self, level_num):
        '''
        Get level by number
        '''
        if not level_num:
            return None

        for level in self._levels:
            if level.level_num == level_num:
                return level()
        return None

    def search(self, path):
        '''
        Search a path for levels
        '''
        for (dirpath, dirnames, filenames) in os.walk(path):
            LOGGER.debug("scanning directory for levels: %s", dirpath)
            if '__pycache__' in dirnames:
                dirnames.remove('__pycache__')

            if "__init__.py" in filenames:
                filenames.remove('__init__.py')
                level = self._discover_level(os.path.join(dirpath, "__init__.py"))
                if level:
                    LOGGER.debug("found level in __init__.py; skipping all child directories: %s", path)
                    dirnames.clear()
                    filenames.clear()
                    self._levels.append(LevelStub(level))

            for filename in filenames:
                LOGGER.debug("found file: %s", filename)
                path = os.path.join(dirpath, filename)

                if filename.endswith(".py"):
                    level = self._discover_level(path)
                    self._levels.append(LevelStub(level))
                    LOGGER.debug("Levels: %s", self._levels)

    def add_search_path(self, path):
        '''
        Add a path to search and search it for levels
        '''
        self.paths.append(path)
        self.search(path)

    def reload(self):
        '''
        Reload the levels
        '''
        self._levels = []
        for path in self.paths:
            self.search(path)

    def _discover_level(self, path):  # pylint: disable=R0201
        '''
        Private method used to discover and return the level found in a file
        '''
        loader = SourceFileLoader(str(uuid4()).replace('-', ''), path)

        try:
            mod = types.ModuleType(loader.name)
            mod.__file__ = path
            loader.exec_module(mod)
        except BaseException as exc:
            LOGGER.exception("file is not a valid Python module: %s. %s.", path, str(exc))
            return None

        if hasattr(mod, '__Level__'):
            # pylint: disable=E1101
            level = mod.__Level__
            LOGGER.debug("found level: %s", path)
            return level

        LOGGER.debug("module __Level__ attribute is not defined; file is not a valid level: %s", path)
        return None
