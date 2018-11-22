'''
Game camera
'''


def simple_camera(_screen_size, camera, target_rect):
    '''
    Simple camera implementation - Keeps target centered
    '''
    left, top, _, _ = target_rect
    return [left, top, camera[2], camera[3]]


def complex_camera(screen_size, camera, target_rect):
    '''
    Complex camera implementation - Dynamic camera movement

    TODO: This needs to be fixed to work with JackIT2
    '''
    left, top, _, _ = target_rect
    _, _, width, height = camera
    left, top, _, _ = -left + (screen_size[0] / 2.5), -top + (screen_size[1] / 2.5), width, height

    left = min(0, left)                                   # Stop scrolling at the left edge
    left = max(-(camera[2] - screen_size[0]), left)    # Stop scrolling at the right edge
    top = max(-(camera[3] - screen_size[1]), top)     # Stop scrolling at the bottom
    top = min(0, top)                                     # Stop scrolling at the top
    return [left, top, width, height]


class Camera:
    '''
    Game camera
    '''
    def __init__(self, screen_size, camera_func):
        self.screen_size = screen_size
        self.camera_func = camera_func
        self.pos = [0, 0, self.screen_size[0], self.screen_size[1]]
        self.aspect_ratio = self.screen_size[0] / self.screen_size[1]

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

    def update(self, target):
        '''
        Update camera position based on target position
        '''
        self.pos = self.camera_func(self.screen_size, self.pos, target)

    def get(self):
        '''
        Return the current position of the camera
        '''
        return tuple(self.pos)
