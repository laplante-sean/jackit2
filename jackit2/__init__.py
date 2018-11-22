'''
The main game loop and Qt OpenGL widget implementation
'''
import sys
import time
import logging

from PyQt5 import QtOpenGL, QtWidgets, QtCore

from jackit2.core.engine import GAME_ENGINE
from deploy import SITE_DEPLOYMENT

LOGGER = logging.getLogger(__name__)


class QtOpenGLWidget(QtOpenGL.QGLWidget):
    '''
    Qt OpenGL widget class
    '''
    # pylint: disable=C0103, R0201, R0902

    def __init__(self):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(4, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        fmt.setSwapInterval(1)

        super().__init__(fmt, None)

        # Get the config
        self.config = SITE_DEPLOYMENT.config
        self.framerate = self.config.framerate
        self.skip_ms = 1000.0 / self.framerate  # Max ms a frame can take to work out to be the desired framerate
        self.fps = self.framerate  # Tracks the current FPS

        # Store the default window title and set it
        self.window_title = "JackIT 2.0!"
        self.setWindowTitle(self.window_title)

        # Set a fixed size so the window size cannot be changed during the game
        self.setFixedSize(self.config.width, self.config.height)

        # Start the game timer. Tracks elapsed time
        self.timer = QtCore.QElapsedTimer()
        self.timer.start()
        self.prev_time = self.timer.elapsed()

        # True if development mode is enabled. False otherwise.
        self.dev_mode = self.config.is_development_mode()

        # Prepare to display the FPS and playtime int he window titles
        if self.dev_mode:
            self.setWindowTitle(self.window_title + " - FPS: 0    Playtime: 0")
            self.fpstimer = QtCore.QTimer()
            self.fpstimer.timeout.connect(self.fps_display)
            self.fpstimer.start(1000)

    def fps_display(self):
        '''
        In dev mode this is called every second to display the current FPS
        '''
        # Print framerate and playtime in titlebar.
        text = " - FPS: {0:.2f}   Playtime: {1:.2f}".format(self.fps, self.timer.elapsed() / 1000)
        self.setWindowTitle(self.window_title + text)

    def closeEvent(self, event):
        '''
        Override base class closeEvent
        '''
        LOGGER.debug("closeEvent: %s", str(event))
        GAME_ENGINE.quit()
        event.accept()

    def keyPressEvent(self, event):
        '''
        Handle keypress events
        '''
        LOGGER.debug("keyPressEvent(%d): %s", event.key(), event.text())
        GAME_ENGINE.shoot()

    def mousePressEvent(self, event):
        '''
        Handle mouse click events
        '''
        if not self.dev_mode:
            return

        LOGGER.debug("mousePressEvent(%d): (%d, %d)", event.button(), event.x(), event.y())
        GAME_ENGINE.mouse_press(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        '''
        Handle mouse release events
        '''
        if not self.dev_mode:
            return

        LOGGER.debug("mouseReleaseEvent(%d): (%d, %d)", event.button(), event.x(), event.y())
        GAME_ENGINE.mouse_release(event.x(), event.y())

    def mouseMoveEvent(self, event):
        '''
        Handle mouse move events. These are only caught if a button is being held
        '''
        if not self.dev_mode:
            return

        LOGGER.debug("mouseMoveEvent(%d, %d)", event.x(), event.y())
        GAME_ENGINE.mouse_move(event.x(), event.y())

    def wheelEvent(self, event):
        '''
        Handle mouse wheel events.
        '''
        if not self.dev_mode:
            return

        LOGGER.debug("wheelEvent(%d, %d)", event.angleDelta().x(), event.angleDelta().y())
        GAME_ENGINE.mouse_wheel(event.angleDelta().y())

    def initializeGL(self):
        '''
        Initialize OpenGL
        '''
        LOGGER.debug("initializeGL()")
        GAME_ENGINE.setup(self)
        self.prev_time = self.timer.elapsed()

    def paintGL(self):
        '''
        Update the window
        '''
        # Keep a constant framerate
        cur_time = self.timer.elapsed()
        time_bw_frames = cur_time - self.prev_time  # How much time b/w last frame and this frame

        # How much time do we have to spare still keeping the desired framerate
        sleep_time = self.skip_ms - time_bw_frames
        if sleep_time > 0:
            # Only bother sleeping if we had time to spare
            time.sleep(sleep_time / 1000.0)  # Convert to seconds for sleep()

        # Calculate the framerate
        cur_time = self.timer.elapsed()
        time_bw_frames = cur_time - self.prev_time or 1  # Cannot be 0
        self.fps = (1.0 / time_bw_frames) * 1000  # Multiply by 1000 to get per second
        self.prev_time = self.timer.elapsed()

        # Do the rendering and math and everything
        GAME_ENGINE.update()
        self.update()


def run():
    '''
    Run the game
    '''
    # Put the main window in the middle of the screen
    screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
    MAIN_WINDOW.move(
        (screen.width() - SITE_DEPLOYMENT.config.width) // 2,
        (screen.height() - SITE_DEPLOYMENT.config.height) // 2
    )

    # Show the window and execute the app
    MAIN_WINDOW.show()
    QT_APP.exec_()


QT_APP = QtWidgets.QApplication(sys.argv)
MAIN_WINDOW = QtOpenGLWidget()
