from unittest import TestCase
from unittest.mock import patch, mock_open

from jackit2.config import (
    JackitConfig, ConfigError, validate_bool,
    validate_color, validate_int, validate_ubyte,
    validate_uint
)

CONFIG_BAD_JSON = '''
{"blerp"{
'''


class TestValidators(TestCase):
    valid_trues = ["1", "true", "t", "yes", "on"]
    valid_falses = ["0", "false", "f", "no", "off"]

    def test_validate_bool_wrong_type(self):
        with self.assertRaises(ConfigError):
            validate_bool({})

    def test_validate_bool_wrong_str(self):
        with self.assertRaises(ConfigError):
            validate_bool("ferp")

    def test_validate_bool_str(self):
        for b in self.valid_trues:
            self.assertTrue(validate_bool(b))
        for b in self.valid_falses:
            self.assertFalse(validate_bool(b))

    def test_validate_bool_case_insensitive(self):
        self.assertTrue(validate_bool("TRUE"))
        self.assertFalse(validate_bool("FALSE"))

    def test_validate_bool_bool(self):
        self.assertTrue(validate_bool(True))
        self.assertFalse(validate_bool(False))

    def test_validate_int_wrong_type(self):
        with self.assertRaises(ConfigError):
            validate_int({})

    def test_validate_int_wrong_str(self):
        with self.assertRaises(ConfigError):
            validate_int("fish")

    def test_validate_int_str(self):
        self.assertEqual(validate_int("10"), 10)
        with self.assertRaises(ConfigError):
            validate_int("6.66")

    def test_validate_int_int(self):
        self.assertEqual(validate_int(10), 10)

    def test_validate_uint(self):
        with self.assertRaises(ConfigError):
            validate_uint(-10)
        self.assertEqual(validate_uint(10), 10)

    def test_validate_ubyte(self):
        with self.assertRaises(ConfigError):
            validate_ubyte(-10)
        with self.assertRaises(ConfigError):
            validate_ubyte(256)

        self.assertEqual(validate_ubyte(225), 225)

    def test_validate_color(self):
        with self.assertRaises(ConfigError):
            validate_color({})
        with self.assertRaises(ConfigError):
            validate_color(["10", "20"])

        self.assertEqual(validate_color((0, 255, 0)), (0, 255, 0))


class TestConfig(TestCase):
    valid_modes = ["production", "development", "dev", "debug"]

    def setUp(self):
        self.config = JackitConfig("test.site.cfg.json")

    def test_mode(self):
        self.assertEqual(self.config.mode, "production")  # Test the default
        self.assertFalse(self.config.is_development_mode())

        with self.assertRaises(ConfigError):
            self.config.mode = "fish"

        for mode in self.valid_modes:
            self.config.mode = mode

        self.assertTrue(self.config.is_development_mode())

    @patch('builtins.open', new_callable=mock_open, read_data=CONFIG_BAD_JSON)
    def test_config_load_bad_json(self, mock_file):
        with self.assertRaises(ConfigError):
            self.config.load()

    @patch('builtins.open', new_callable=mock_open)
    def test_config_load_no_exist(self, mock_file):
        mock_file.side_effect = IOError("File not found")
        with self.assertRaises(ConfigError):
            self.config.load()

    @patch('builtins.open', new_callable=mock_open)
    def test_config_save_access_denied(self, mock_file):
        mock_file.side_effect = IOError("Access Denied")
        with self.assertRaises(ConfigError):
            self.config.save()
