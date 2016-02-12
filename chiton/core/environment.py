from voluptuous import All, Length, MultipleInvalid, Schema

from chiton.core.exceptions import ConfigurationError


def use_config(user_data={}):
    """Load an external JSON configuration file.

    The contents of the JSON file are deeply merged with the defaults, ensuring
    that the returned value is always valid.

    Args:
        user_data (dict): The user customizations to apply to the base configuration

    Returns:
        dict: The merged configuration file

    Raises:
        chiton.core.exceptions.ConfigurationError: If the user settings are invalid
    """
    try:
        _validate_config(user_data)
    except MultipleInvalid as e:
        raise ConfigurationError("Invalid configuration: %s" % e)

    config_data = _default_config()
    config_data.update(user_data)

    return config_data


def _default_config():
    """Define the default configuration data."""
    return {
        "allowed_hosts": [],
        "database": {},
        "debug": False,
        "secret_key": None,
        "static_url": "/static/"
    }


def _validate_config(config):
    """Validate configuration data, raising an error for invalid data."""
    Schema({
        "allowed_hosts": [str],
        "database": Schema({
            "engine": All(str, Length(min=1)),
            "host": All(str, Length(min=1)),
            "name": All(str, Length(min=1)),
            "password": All(str, Length(min=1)),
            "port": All(int),
        }),
        "debug": bool,
        "secret_key": All(str, Length(min=1)),
        "static_url": All(str, Length(min=1), _MediaUrl())
    })(config)


def _MediaUrl():
    """Ensure that a URL is a Django-style media URL ending in a slash."""
    def validator(value):
        if not value.endswith("/"):
            raise ValueError("%s does not have a trailing slash" % value)
    return validator
