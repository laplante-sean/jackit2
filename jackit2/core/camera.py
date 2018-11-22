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


def complex_camera(_screen_size, level_size, camera, target_rect):
    '''
    Complex camera implementation - Dynamic camera movement around a level
    '''
    level_width, level_height = level_size
    left, top, _, _ = target_rect
    _, _, width, height = camera
    left, top = -left + (level_width / 2.5), -top + (level_height / 2.5)

    left = min(0, left)                           # Stop scrolling at the left edge
    left = max(-(width - level_width), left)      # Stop scrolling at the right edge
    top = max(-(height - level_height), top)      # Stop scrolling at the bottom
    top = min(0, top)                             # Stop scrolling at the top
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
        self.pos = self.camera_func(self.screen_size, self.level_size, self.pos, target)

    def get(self):
        '''
        Return the current position of the camera
        '''
        return tuple(self.pos)
