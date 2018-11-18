'''
The main game loop
'''
import sys
import logging

from PyQt5 import QtOpenGL, QtWidgets, QtCore

from jackit2.core.engine import GAME_ENGINE
from deploy import SITE_DEPLOYMENT

LOGGER = logging.getLogger(__name__)


class QtOpenGLWidget(QtOpenGL.QGLWidget):
    '''
    Qt OpenGL widget class
    '''
    # pylint: disable=C0103, R0201

    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(4, 1)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        fmt.setSwapInterval(1)

        super().__init__(fmt, None)

        # Get the config
        self.config = SITE_DEPLOYMENT.config

        # Store the default window title and set it
        self.window_title = "JackIT 2.0!"
        self.setWindowTitle(self.window_title)

        # Set a fixed size so the window size cannot be changed during the game
        self.setFixedSize(self.config.width, self.config.height)

        # Start the game timer. Tracks elapsed time
        self.timer = QtCore.QElapsedTimer()
        self.timer.start()

        # Prepare the FPS timer and callback for dev mode only
        if self.config.is_development_mode():
            self.setWindowTitle(self.window_title + " - FPS: 0    Playtime: 0")
            self.fps = 0  # Tracks the current FPS
            self.fpstimer = QtCore.QTimer()
            self.fpstimer.timeout.connect(self.display_info)
            self.fpstimer.start(1000)  # Timeout every second

    def display_info(self):
        '''
        Display some info in the window title
        '''
        # Print framerate and playtime in titlebar.
        text = " - FPS: {0:.2f}   Playtime: {1:.2f}".format(self.fps, (self.timer.elapsed() / 1000))
        self.setWindowTitle(self.window_title + text)
        self.fps = 0  # Reset to 0 every second

    def closeEvent(self, event):
        '''
        Override base class closeEvent
        '''
        LOGGER.debug("closeEvent: %s", str(event))
        GAME_ENGINE.quit()
        event.accept()

    def keyPressEvent(self, event):
        '''
        Handle keyboard events
        '''
        LOGGER.debug("keyPressEvent(%d): %s", event.key(), event.text())
        GAME_ENGINE.shoot()

    def initializeGL(self):
        '''
        Initialize OpenGL
        '''
        LOGGER.debug("initializeGL()")
        GAME_ENGINE.setup(self.width(), self.height())

    def paintGL(self):
        '''
        Update the window
        '''
        if self.config.is_development_mode():
            #: In dev mode, increment the frame counter
            self.fps += 1

        GAME_ENGINE.update((self.timer.elapsed() / 1000))
        self.update()


def run():
    '''
    Run the game
    '''
    MAIN_WINDOW.show()
    QT_APP.exec_()


QT_APP = QtWidgets.QApplication(sys.argv)
MAIN_WINDOW = QtOpenGLWidget()
