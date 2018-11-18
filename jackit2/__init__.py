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

        self.timer = QtCore.QElapsedTimer()
        self.timer.start()

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
        LOGGER.debug("keyPressEvent: %s", str(event))
        GAME_ENGINE.shoot()

    def initializeGL(self):
        '''
        Initialize OpenGL
        '''
        LOGGER.debug("initializeGL")
        GAME_ENGINE.setup()

    def paintGL(self):
        '''
        Update the window
        '''
        GAME_ENGINE.update((0, 0, self.width(), self.height()), self.timer.elapsed() / 1000)
        self.update()


def run():
    '''
    Run the game
    '''
    MAIN_WINDOW.resize(SITE_DEPLOYMENT.config.width, SITE_DEPLOYMENT.config.height)
    MAIN_WINDOW.show()
    QT_APP.exec_()


QT_APP = QtWidgets.QApplication(sys.argv)
MAIN_WINDOW = QtOpenGLWidget()
