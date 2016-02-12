from unittest import TestCase

from chiton.core.environment import use_config
from chiton.core.exceptions import ConfigurationError


class UseConfigTestCase(TestCase):

    def test_default(self):
        """It produces a default configuration dict when given no arguments."""
        config = use_config()
        self.assertIsInstance(config, dict)

    def test_user_merge(self):
        """It merges the user options with the defaults."""
        config = use_config({"secret_key": "secret"})

        self.assertEqual(config["secret_key"], "secret")
        self.assertIn("debug", config)

    def test_invalid_setting(self):
        """It raises a custom error when user settings contain an unknown value."""
        with self.assertRaises(ConfigurationError):
            use_config({"unknown_value": True})

    def test_invalid_setting_value(self):
        """It raises a custom error when the configuration file defines an invalid value for a setting."""
        with self.assertRaises(ConfigurationError):
            use_config({"secret_key": None})

    def test_allowed_hosts(self):
        """It expects hosts to be a list of strings."""
        config = use_config({"allowed_hosts": ["localhost"]})
        self.assertEqual(config["allowed_hosts"], ["localhost"])

        with self.assertRaises(ConfigurationError):
            use_config({"allowed_hosts": "localhost"})

    def test_allowed_hosts_default(self):
        """It defaults to an empty list of hosts."""
        config = use_config()
        self.assertEqual(config["allowed_hosts"], [])

    def test_debug(self):
        """It expects a boolean value for the debug state."""
        config = use_config({"debug": True})
        self.assertEqual(config["debug"], True)

        with self.assertRaises(ConfigurationError):
            use_config({"debug": 1})

    def test_debug_default(self):
        """It defaults to disabled debug mode."""
        config = use_config()
        self.assertEqual(config["debug"], False)

    def test_database_default(self):
        """It defaults to an empty database dict."""
        config = use_config()
        self.assertEqual(config["database"], {})

    def test_database_minimal(self):
        """It accepts minimal database information."""
        config = use_config({
            "database": {
                "engine": "sqlite3",
                "name": "test.sqlite3"
            }
        })

        self.assertEqual(config["database"]["engine"], "sqlite3")
        self.assertEqual(config["database"]["name"], "test.sqlite3")

    def test_database_full(self):
        """It accepts a full database configuration."""
        config = use_config({
            "database": {
                "engine": "postgresql",
                "host": "localhost",
                "name": "test",
                "password": "secret",
                "port": 1234
            }
        })

        self.assertEqual(config["database"]["name"], "test")

    def test_database_validation(self):
        """It expects non-empty strings for all non-port parameters."""
        for param in ["engine", "host", "name", "password"]:
            config = use_config({"database": {param: "valid"}})
            self.assertEqual(config["database"][param], "valid")

            with self.assertRaises(ConfigurationError):
                use_config({"database": {param: ""}})

    def test_database_port(self):
        """It expects a numeric database port."""
        config = use_config({"database": {"port": 1234}})
        self.assertEqual(config["database"]["port"], 1234)

        with self.assertRaises(ConfigurationError):
            use_config({"database": {"port": "1234"}})

    def test_secret_key(self):
        """It expects a non-empty string for the secret key."""
        config = use_config({"secret_key": "secret"})
        self.assertEqual(config["secret_key"], "secret")

        with self.assertRaises(ConfigurationError):
            use_config({"secret_key": ""})

    def test_secret_key_default(self):
        """It defaults to a null value for the secret key."""
        config = use_config()
        self.assertIsNone(config["secret_key"])

    def test_static_url(self):
        """It expects a non-empty string for the static URL."""
        config = use_config({"static_url": "/assets/"})
        self.assertEqual(config["static_url"], "/assets/")

        with self.assertRaises(ConfigurationError):
            use_config({"static_url": ""})

    def test_static_url_trailing_slash(self):
        """It expects the static URL to use a trailing slash."""
        config = use_config({"static_url": "/assets/"})
        self.assertEqual(config["static_url"], "/assets/")

        with self.assertRaises(ConfigurationError):
            use_config({"static_url": "/assets"})

    def test_static_url_root_path(self):
        """It allows a static URL to be the root path."""
        config = use_config({"static_url": "/"})
        self.assertEqual(config["static_url"], "/")

    def test_static_url_absolute_url(self):
        """It allows a static URL to be an absolute URL."""
        config = use_config({"static_url": "http://example.com/"})
        self.assertEqual(config["static_url"], "http://example.com/")
