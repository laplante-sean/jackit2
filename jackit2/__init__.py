'''
The main game loop and Qt OpenGL widget implementation
'''
import sys
import time
import logging

from PyQt5 import QtOpenGL, QtWidgets, QtCore

from jackit2.util import get_game_engine, get_config
from jackit2.core.input import InputEventType

LOGGER = logging.getLogger(__name__)


class QtOpenGLWidget(QtOpenGL.QGLWidget):
    '''
    Qt OpenGL widget class
    '''
    # pylint: disable=C0103, R0902

    def __init__(self, config):
        # Create the format
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(4, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        fmt.setSwapInterval(1)

        # Set the format in the parent class
        super().__init__(fmt, None)

        self.framerate = config.framerate
        self.skip_ms = 1000.0 / self.framerate  # Max ms a frame can take to work out to be the desired framerate
        self.fps = self.framerate  # Tracks the current FPS

        # Store the default window title and set it
        self.window_title = "JackIT 2.0!"
        self.setWindowTitle(self.window_title)

        # Set a fixed size so the window size cannot be changed during the game
        self.setFixedSize(config.width, config.height)

        # Put the main window in the middle of the screen
        screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.move((screen.width() - config.width) // 2, (screen.height() - config.height) // 2)

        # Start the game timer. Tracks elapsed time
        self.timer = QtCore.QElapsedTimer()
        self.timer.start()
        self.prev_time = self.timer.elapsed()

        # True if development mode is enabled. False otherwise.
        self.dev_mode = config.is_development_mode()

        # Get the game engine
        self.game_engine = get_game_engine()

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
        self.game_engine.quit()
        event.accept()

    def keyPressEvent(self, event):
        '''
        Handle keypress events
        '''
        LOGGER.debug("keyPressEvent(%d): %s", event.key(), event.text())
        self.game_engine.handle_input_event(event, event_type=InputEventType.KEY_PRESS)

    def keyReleaseEvent(self, event):
        '''
        Handle key release events
        '''
        LOGGER.debug("keyReleaseEvent(%d): %s", event.key(), event.text())
        self.game_engine.handle_input_event(event, event_type=InputEventType.KEY_RELEASE)

    def mousePressEvent(self, event):
        '''
        Handle mouse click events
        '''
        LOGGER.debug("mousePressEvent(%d): (%d, %d)", event.button(), event.x(), event.y())
        self.game_engine.handle_input_event(event, event_type=InputEventType.MOUSE_PRESS)

    def mouseReleaseEvent(self, event):
        '''
        Handle mouse release events
        '''
        LOGGER.debug("mouseReleaseEvent(%d): (%d, %d)", event.button(), event.x(), event.y())
        self.game_engine.handle_input_event(event, event_type=InputEventType.MOUSE_RELEASE)

    def mouseMoveEvent(self, event):
        '''
        Handle mouse move events. These are only caught if a button is being held
        '''
        LOGGER.debug("mouseMoveEvent(%d, %d)", event.x(), event.y())
        self.game_engine.handle_input_event(event, event_type=InputEventType.MOUSE_MOVE)

    def wheelEvent(self, event):
        '''
        Handle mouse wheel events.
        '''
        LOGGER.debug("wheelEvent(%d, %d)", event.angleDelta().x(), event.angleDelta().y())
        self.game_engine.handle_input_event(event, event_type=InputEventType.MOUSE_WHEEL)

    def initializeGL(self):
        '''
        Initialize OpenGL
        '''
        LOGGER.debug("initializeGL()")
        self.game_engine.setup(self.width(), self.height(), self.framerate)
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
        self.game_engine.update()
        self.update()


def run():
    '''
    Run the game
    '''
    MAIN_WINDOW.show()
    QT_APP.exec_()


QT_APP = QtWidgets.QApplication(sys.argv)
MAIN_WINDOW = QtOpenGLWidget(get_config())
