'''
Game camera
'''


def simple_camera(_screen_size, _level_size, camera, target_rect):
    '''
    Simple camera implementation - Keeps target centered
    '''
    left, top, _, _ = target_rect
    _, _, width, height = camera
    return [left, top, width, height]  # Center the object


def complex_camera(_screen_size, level_size, camera, target_rect):  # pylint: disable=R0914
    '''
    Complex camera implementation - Dynamic camera movement around a level
    '''
    level_width, level_height = level_size
    left, top, _, _ = target_rect
    cam_x, cam_y, width, height = camera

    # Get the edges of the camera
    cam_left_edge = cam_x - width
    cam_right_edge = cam_x + width
    cam_top_edge = cam_y + height
    cam_bottom_edge = cam_y - height

    # Get the left bottom edges of the level
    # The right and top edges are just the width and height
    left_edge = cam_x - cam_left_edge
    bottom_edge = cam_y - cam_bottom_edge

    left = min((cam_x - (cam_right_edge - level_width)), left)      # Stop scrolling at the right edge
    left = max(left_edge, left)                                     # Stop scrolling at the left edge
    top = min((cam_y - (cam_top_edge - level_height)), top)         # Stop scrolling at the top
    top = max(bottom_edge, top)                                     # Stop scrolling at the bottom
    return [left, top, width, height]


class Camera:
    '''
    Game camera
    '''
    def __init__(self, screen_size, camera_func):
        self.screen_size = screen_size
        self.level_size = (0, 0)
        self.camera_func = camera_func
        self.pos = [0, 0, self.screen_size[0], self.screen_size[1]]
        self.aspect_ratio = self.screen_size[0] / self.screen_size[1]

    def load_level(self, level_size):
        '''
        Sets the level size when a level is loaded
        '''
        self.level_size = level_size

    def move(self, delta_x, delta_y):
        '''
        Move the camera
        '''
        self.pos[0] += delta_x
        self.pos[1] += delta_y

    def zoom(self, delta):
        '''
        Zoom the camera in or out
        '''
        self.pos[2] += delta * self.aspect_ratio
        self.pos[3] += delta

    def reset(self):
        '''
        Reset the camera position
        '''
        self.pos = [0, 0, self.screen_size[0], self.screen_size[1]]

    def update(self, target):
        '''
        Update camera position based on target position
        '''
        self.pos = self.camera_func(
            self.screen_size, self.level_size, self.pos,
            (target.x_pos, target.y_pos, target.width, target.height)
        )

    def draw(self, program):
        '''
        Draw the camera
        '''
        program['Camera'].value = tuple(self.pos)
