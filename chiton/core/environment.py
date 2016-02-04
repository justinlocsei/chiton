import json
from voluptuous import All, Required, Length, MultipleInvalid, Optional, Schema

from chiton.core.exceptions import ConfigurationError

DEFAULT_CONFIG = {
    "allowed_hosts": [],
    "debug": False,
    "secret_key": None,
    "static_url": "/static/"
}

CONFIG_VALIDATOR = Schema({
    Optional("allowed_hosts"): [str],
    Optional("debug"): bool,
    Required("secret_key"): All(str, Length(min=32)),
    Optional("static_url"): All(str, Length(min=1))
})


def load_config(path):
    """Load an external JSON configuration file.

    The contents of the JSON file are deeply merged with the defaults, ensuring
    that the returned value is always valid.

    Args:
        path (str): An absolute path to a JSON configuration file

    Returns:
        chiton.core.environment.Configuration: The parsed configuration file
    """
    with open(path) as json_config:
        config = json.load(json_config)

    return config


class Configuration(object):
    """Configuration for an environment."""

    def __init__(self, settings):
        self._config = self._apply_to_defaults(settings)

        validation_error = self._validate(self._config)
        if validation_error:
            raise ConfigurationError(validation_error)

    def _apply_to_defaults(self, settings):
        """Create a dict combining the user values and the default values."""
        merged = DEFAULT_CONFIG.copy()
        merged.update(settings)
        return merged

    def _validate(self, settings):
        """Validate the settings, returning an error when they are invalid."""
        try:
            CONFIG_VALIDATOR(settings)
        except MultipleInvalid as e:
            return e
        else:
            return None
