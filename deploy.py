'''
Handles initial setup and tracking of useful globals
'''

import os
import sys
import logging

from jackit2.config import JackitConfig


class SiteDeploymentSingleton:
    '''
    Handles initial setup
    '''
    # pylint: disable=R0902

    _instance = None

    @classmethod
    def instance(cls):
        '''
        Get instance of SiteDeploymentSingleton
        '''
        if cls._instance is None:
            cls._instance = SiteDeploymentSingleton()
            return cls._instance
        return cls._instance

    def __init__(self):
        from jackit2.util import get_level_loader

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.base_path, "jackit2", "resources")
        self.texture_path = os.path.join(self.resource_path, 'textures')
        self.audio_path = os.path.join(self.resource_path, "audio")
        self.config_path = os.path.join(self.base_path, "site.cfg.json")
        self.builtin_levels = os.path.join(self.base_path, "jackit2", "levels")
        self.contrib_levels = os.path.join(self.base_path, "contrib")
        self.loader = get_level_loader()
        self._config = None
        self._setup_config()
        self._setup_logging()
        self.loader.add_search_path(self.builtin_levels)
        self.loader.add_search_path(self.contrib_levels)

    @property
    def config(self):
        '''
        Config getter
        '''
        return self._config

    def _setup_logging(self):
        '''
        Setup the root logger
        '''
        root_logger = logging.getLogger()

        if self.config.is_development_mode():
            root_logger.setLevel(logging.DEBUG)
            log_stdout_handler = logging.StreamHandler(sys.stdout)
            log_stdout_handler.setLevel(logging.DEBUG)
            root_logger.addHandler(log_stdout_handler)

    def _setup_config(self):
        '''
        Setup the config file
        '''
        self._config = JackitConfig(self.config_path)
        if os.path.exists(self.config_path):
            self._config.load()
        self._config.save()


SITE_DEPLOYMENT = SiteDeploymentSingleton.instance()
