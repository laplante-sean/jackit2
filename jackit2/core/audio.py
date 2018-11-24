'''
Does the sound for the game
'''

import os
import logging

import pygame

from deploy import SITE_DEPLOYMENT

LOGGER = logging.getLogger(__name__)


class GameMusic:
    '''
    Handles all the sound for the game
    '''

    def __init__(self):
        pygame.init()
        game_music_path = os.path.join(SITE_DEPLOYMENT.audio_path, "music", "music.mp3")
        self.music_loaded = False

        try:
            pygame.mixer.music.load(game_music_path)
            self.music_loaded = True
        except BaseException as exc:
            LOGGER.exception("Unable to load music: %s", str(exc))
            self.music_loaded = False

        self.playing = False

    def is_playing(self):
        '''
        Getter for instance variable playing
        '''
        return self.playing

    def play_game_music(self):
        '''
        Play the game music
        '''
        if not self.music_loaded:
            return

        pygame.mixer.music.play(loops=-1)
        self.playing = True

    def pause_game_music(self):
        '''
        Pause the game music
        '''
        if not self.music_loaded:
            return

        pygame.mixer.music.pause()
        self.playing = False

    def toggle_game_music(self):
        '''
        Toggle the game music on and off
        '''
        if not self.music_loaded:
            return

        if self.is_playing():
            self.pause_game_music()
        else:
            self.play_game_music()
