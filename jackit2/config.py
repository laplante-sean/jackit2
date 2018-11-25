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
        raise ConfigError("Unknown type for object. Expecting 'int', got: {}".format(type(value)))


def validate_float(value):
    '''
    Validagte a float value
    '''
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            raise ConfigError("Invalid float value: {}".format(value))
    elif isinstance(value, int):
        return float(value)
    elif isinstance(value, float):
        return value
    else:
        raise ConfigError("Unknown type for object. Expecting 'float', got: {}".format(type(value)))


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
        self.width = 800
        self.height = 600
        self.framerate = 60
        self.music_enabled = True
        self.high_dpi_scaling = 100.0

        self._mode = None
        self.mode = "production"

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
            "framerate": self.framerate,
            "music_enabled": self.music_enabled,
            "high_dpi_scaling": self.high_dpi_scaling
        }

    def from_json(self, raw):
        '''
        Load values from JSON
        '''
        self.mode = raw.get("mode", "production")
        self.framerate = validate_uint(raw.get("framerate", 60))
        self.music_enabled = validate_bool(raw.get("music_enabled", True))
        self.high_dpi_scaling = validate_float(raw.get("high_dpi_scaling", 100.0))

        # Get resolution
        res = raw.get("resolution", {"width": 800, "height": 600})
        self.width = validate_uint(res.get("width", 800))
        self.height = validate_uint(res.get("height", 600))

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
