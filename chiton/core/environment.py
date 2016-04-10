import os.path
import re

from voluptuous import All, Length, MultipleInvalid, Schema

from chiton.core.exceptions import ConfigurationError


# All known log levels
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


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
        'admins': [],
        'allowed_hosts': [],
        'amazon_associates_aws_access_key_id': None,
        'amazon_associates_aws_secret_access_key': None,
        'amazon_associates_tracking_id': None,
        'backups_aws_access_key_id': None,
        'backups_aws_secret_access_key': None,
        'database': {},
        'debug': False,
        'file_logging': False,
        'log_file': None,
        'log_level': 'INFO',
        'secret_key': None,
        'server_email': None,
        'shopstyle_uid': None,
        'static_root': None,
        'static_url': '/static/'
    }


def _validate_config(config):
    """Validate configuration data, raising an error for invalid data."""
    Schema({
        'admins': [Schema({
            'email': All(str, Length(min=1)),
            'name': All(str, Length(min=1)),
        })],
        'allowed_hosts': [str],
        'amazon_associates_aws_access_key_id': All(str, Length(min=1)),
        'amazon_associates_aws_secret_access_key': All(str, Length(min=1)),
        'amazon_associates_tracking_id': All(str, Length(min=1), _AmazonAssociatesTrackingID()),
        'backups_aws_access_key_id': All(str, Length(min=1)),
        'backups_aws_secret_access_key': All(str, Length(min=1)),
        'backups_s3_bucket': All(str, Length(min=1)),
        'database': Schema({
            'engine': All(str, Length(min=1)),
            'host': All(str, Length(min=1)),
            'name': All(str, Length(min=1)),
            'password': All(str, Length(min=1)),
            'port': All(int),
            'user': All(str, Length(min=1))
        }),
        'debug': bool,
        'file_logging': bool,
        'log_file': All(str, Length(min=1), _AbsolutePath()),
        'log_level': All(str, Length(min=1), _LogLevel()),
        'secret_key': All(str, Length(min=1)),
        'server_email': All(str, Length(min=1)),
        'shopstyle_uid': All(str, Length(min=1)),
        'static_root': All(str, Length(min=1), _AbsolutePath()),
        'static_url': All(str, Length(min=1), _MediaUrl())
    })(config)


def _AbsolutePath():
    """Ensure that a string is an absolute file path."""
    def validator(value):
        if not os.path.isabs(value):
            raise ValueError('%s must be an absolute path' % value)
    return validator


def _AmazonAssociatesTrackingID():
    """Ensure that a string is an Amazon Associates tracking ID."""
    def validator(value):
        if not re.search('-2\d$', value):
            raise ValueError('%s must be an Amazon Associates tracking ID' % value)
    return validator


def _LogLevel():
    """Ensure that a string is a known log level."""
    def validator(value):
        if value not in LOG_LEVELS:
            raise ValueError('%s must be a log level (%s)' % (value, ', '.join(LOG_LEVELS)))
    return validator


def _MediaUrl():
    """Ensure that a URL is a Django-style media URL ending in a slash."""
    def validator(value):
        if not value.endswith('/'):
            raise ValueError('%s does not have a trailing slash' % value)
    return validator
