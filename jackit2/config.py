'''
Config for jackit
'''

import json
import logging

LOGGER = logging.getLogger(__name__)


class ConfigError(Exception):
    '''
    Error during loading/saving/parsing of JSON config
    '''
    pass


def validate_bool(value):
    '''
    Validate a boolean value
    '''
    if isinstance(value, str):
        if value.lower() not in ("1", "0", "true", "false", "t", "f", "yes", "no", "on", "off"):
            raise ConfigError("Invalid boolean value: {}".format(value))
        elif value.lower() in ("1", "true", "t", "yes", "on"):
            return True
        else:
            return False
    elif isinstance(value, bool):
        return value
    else:
        raise ConfigError("Unknown type for object. Expecting bool, got {}".format(type(value)))


def validate_int(value):
    '''
    Validate an integer value
    '''
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ConfigError("Invalid integer value: {}".format(value))
    elif isinstance(value, int):
        return value
    else:
        raise ConfigError("Unknown type object. Expecting 'int', got: {}".format(type(value)))


def validate_uint(value):
    '''
    Validate an unsigned integer
    '''
    value = validate_int(value)
    if value < 0:
        raise ConfigError("Expected an unsigned integer. Got a negative number")
    return value


def validate_ubyte(value):
    '''
    Validate an unsigned byte value
    '''
    value = validate_int(value)
    if value < 0 or value > 255:
        raise ConfigError("Unsigned byte must be between 0 and 255 inclusive")
    return value


def validate_color(value):
    '''
    Validate a color value from the config
    '''
    if isinstance(value, (list, tuple)):
        if len(value) != 3:
            raise ConfigError("Colors must be tuples of 3 values representing R, G, B")

        new_list = []
        for color_val in value:
            new_list.append(validate_ubyte(color_val))

        return tuple(new_list)

    raise ConfigError("Colors must be a list or tuple of 3 unsigned byte values")


class JackitConfig:
    '''
    Jackit2 config class
    '''
    # pylint: disable=R0902

    def __init__(self, path):
        self.path = path
        self._width = 800
        self._height = 600
        self._framerate = 60
        self._mode = "production"
        self._fullscreen = False
        self.sound_enabled = True

    @property
    def mode(self):
        '''
        Handles getting the value of mode
        '''
        return self._mode

    @mode.setter
    def mode(self, value):
        '''
        Handles setting mode and validating the value
        '''
        if value not in ("production", "development", "dev", "debug"):
            raise ConfigError(
                "Invalid mode {}. Expected one of: production, development, dev, or debug".format(
                    value
                )
            )

        self._mode = value

    @property
    def fullscreen(self):
        '''
        Get current value of fullscreen
        '''
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, value):
        '''
        Set the value of fullscreen and validate
        '''
        self._fullscreen = validate_bool(value)

    @property
    def width(self):
        '''
        Get the current value of width
        '''
        return self._width

    @width.setter
    def width(self, value):
        '''
        Set the value of width and validate
        '''
        self._width = validate_uint(value)

    @property
    def height(self):
        '''
        Get the value of height
        '''
        return self._height

    @height.setter
    def height(self, value):
        '''
        Set the value of height and validate
        '''
        self._height = validate_uint(value)

    @property
    def framerate(self):
        '''
        Get the value of framerate
        '''
        return self._framerate

    @framerate.setter
    def framerate(self, value):
        '''
        Set the value of framerate and validate
        '''
        self._framerate = validate_uint(value)

    def to_json(self):
        '''
        JSON representation of config options
        '''
        return {
            "resolution": {
                "width": self.width,
                "height": self.height
            },
            "mode": self.mode,
            "fullscreen": self.fullscreen,
            "framerate": self.framerate,
            "sound_enabled": self.sound_enabled,
        }

    def from_json(self, raw):
        '''
        Load values from JSON
        '''
        self.mode = raw.get("mode", "production")
        res = raw.get("resolution", {"width": 800, "height": 600})
        self.width = res.get("width", 800)
        self.height = res.get("height", 600)
        self.fullscreen = raw.get("fullscreen", False)
        self.framerate = raw.get("framerate", 60)
        self.sound_enabled = validate_bool(raw.get("sound_enabled", True))

    def load(self):
        '''
        Load the config file
        '''
        try:
            with open(self.path, 'r') as config_file:
                self.from_json(json.loads(config_file.read()))
        except json.JSONDecodeError:
            raise ConfigError("Unable to load config file. Invalid JSON")
        except IOError as exc:
            raise ConfigError("Could not access file {}. {}".format(self.path, str(exc)))
        except BaseException as exc:  # pragma: no cover
            raise ConfigError("Unknown error loading config: {}".format(str(exc)))

    def save(self):
        '''
        Save config file
        '''
        try:
            with open(self.path, 'w') as config_file:
                config_file.write(json.dumps(self.to_json(), sort_keys=True, separators=(',', ': '), indent=4))
        except IOError as exc:
            raise ConfigError("Could not access file {}. {}".format(self.path, str(exc)))
        except BaseException as exc:  # pragma: no cover
            raise ConfigError("Unknown error saving config: {}".format(str(exc)))

    def is_development_mode(self):
        '''
        Check if the current config is development
        '''
        return self.mode in ("development", "debug", "dev")
