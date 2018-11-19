'''
Classes to deal with playing music and sounds
'''

import os
import logging

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent

from deploy import SITE_DEPLOYMENT

LOGGER = logging.getLogger(__name__)


class GameMusic:
    '''
    Play game music
    '''

    def __init__(self, parent):
        self.player = QMediaPlayer(parent)
        self.player.stateChanged.connect(self.state_changed)
        self.game_music_path = os.path.join(SITE_DEPLOYMENT.audio_path, "music", "music.mp3")
        self.game_music_url = QUrl.fromLocalFile(self.game_music_path)
        self.player.setMedia(QMediaContent(self.game_music_url))
        self.player.setVolume(25)

    def state_changed(self, state):
        '''
        Called when the player's state changes
        '''
        if state == QMediaPlayer.StoppedState:
            # If the music stopped. Start it again
            self.play()

    def play(self):
        '''
        Play the game's music
        '''
        self.player.play()


class GameSound:
    '''
    Play a sound
    '''

    def __init__(self, parent):
        self._sounds = {}
        self.load(parent)

    def play(self, name):
        '''
        Play a sound
        '''
        if name not in self._sounds:
            raise KeyError("No sound found with name '{}'".format(name))

        self._sounds[name].play()

    def load(self, parent):
        '''
        Load all the sounds
        '''
        for (dirpath, _, filenames) in os.walk(os.path.join(SITE_DEPLOYMENT.audio_path, "sounds")):
            for filename in filenames:
                if not filename.endswith(".wav"):
                    LOGGER.warning("file '%s' in sounds directory is not a valid sound", filename)
                    continue

                LOGGER.debug("loading sound: %s", filename)
                path = os.path.join(dirpath, filename)
                name = os.path.splitext(filename)[0]  # Grab the filename component w/o file ext.

                if name not in self._sounds:
                    url = QUrl.fromLocalFile(path)
                    self._sounds[name] = QSoundEffect(parent=parent)
                    self._sounds[name].setSource(url)
                    self._sounds[name].setVolume(0.8)
                    self._sounds[name].setLoopCount(1)
                else:
                    LOGGER.warning("texture with name '%s' has already been loaded.", name)
