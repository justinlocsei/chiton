import os.path
import re

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
        raise ConfigurationError('Invalid configuration: %s' % e)

    config_data = _default_config()
    config_data.update(user_data)

    return config_data


def _default_config():
    """Define the default configuration data."""
    return {
        'allowed_hosts': [],
        'database': {},
        'debug': False,
        'secret_key': None,
        'static_root': None,
        'static_url': '/static/',
        'use_https': False
    }


def _validate_config(config):
    """Validate configuration data, raising an error for invalid data."""
    Schema({
        'allowed_hosts': [str],
        'aws_advertising_access_key_id': All(str, Length(min=1)),
        'aws_advertising_associate_tag': All(str, Length(min=1), _AmazonAssociateTag()),
        'aws_advertising_secret_access_key': All(str, Length(min=1)),
        'database': Schema({
            'engine': All(str, Length(min=1)),
            'host': All(str, Length(min=1)),
            'name': All(str, Length(min=1)),
            'password': All(str, Length(min=1)),
            'port': All(int),
            'user': All(str, Length(min=1))
        }),
        'debug': bool,
        'secret_key': All(str, Length(min=1)),
        'static_root': All(str, Length(min=1), _AbsolutePath()),
        'static_url': All(str, Length(min=1), _MediaUrl()),
        'use_https': All(bool)
    })(config)


def _AbsolutePath():
    """Ensure that a string is an absolute file path."""
    def validator(value):
        if not os.path.isabs(value):
            raise ValueError('%s must be an absolute path' % value)
    return validator


def _AmazonAssociateTag():
    """Ensure that a string is an Amazon associate tag."""
    def validator(value):
        if not re.search('-2\d$', value):
            raise ValueError('%s must be an Amazon associate tag' % value)
    return validator


def _MediaUrl():
    """Ensure that a URL is a Django-style media URL ending in a slash."""
    def validator(value):
        if not value.endswith('/'):
            raise ValueError('%s does not have a trailing slash' % value)
    return validator
