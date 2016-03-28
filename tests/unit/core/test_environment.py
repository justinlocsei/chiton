import pytest

from chiton.core.environment import use_config
from chiton.core.exceptions import ConfigurationError


class TestUseConfig:

    def test_default(self):
        """It produces a default configuration dict when given no arguments."""
        config = use_config()
        assert isinstance(config, dict)

    def test_user_merge(self):
        """It merges the user options with the defaults."""
        config = use_config({'secret_key': 'secret'})

        assert config['secret_key'] == 'secret'
        assert 'debug' in config

    def test_invalid_setting(self):
        """It raises a custom error when user settings contain an unknown value."""
        with pytest.raises(ConfigurationError):
            use_config({'unknown_value': True})

    def test_invalid_setting_value(self):
        """It raises a custom error when the configuration file defines an invalid value for a setting."""
        with pytest.raises(ConfigurationError):
            use_config({'secret_key': None})

    def test_allowed_hosts(self):
        """It expects hosts to be a list of strings."""
        config = use_config({'allowed_hosts': ['localhost']})
        assert config['allowed_hosts'] == ['localhost']

        with pytest.raises(ConfigurationError):
            use_config({'allowed_hosts': 'localhost'})

    def test_allowed_hosts_default(self):
        """It defaults to an empty list of hosts."""
        config = use_config()
        assert config['allowed_hosts'] == []

    def test_amazon_associates_aws_access_key_id(self):
        """It expects a non-empty string for the Amazon Associates AWS access key ID."""
        config = use_config({'amazon_associates_aws_access_key_id': 'access'})
        assert config['amazon_associates_aws_access_key_id'] == 'access'

        with pytest.raises(ConfigurationError):
            use_config({'amazon_associates_aws_access_key_id': ''})

    def test_amazon_associates_aws_secret_access_key(self):
        """It expects a non-empty string for the Amazon Associates AWS secret access key."""
        config = use_config({'amazon_associates_aws_secret_access_key': 'secret'})
        assert config['amazon_associates_aws_secret_access_key'] == 'secret'

        with pytest.raises(ConfigurationError):
            use_config({'amazon_associates_aws_secret_access_key': ''})

    def test_amazon_associates_tracking_id(self):
        """It expects a string that ends in a known region ID for the Amazon Associates tracking ID."""
        config = use_config({'amazon_associates_tracking_id': 'tracking-id-20'})
        assert config['amazon_associates_tracking_id'] == 'tracking-id-20'

        with pytest.raises(ConfigurationError):
            use_config({'amazon_associates_tracking_id': 'tracking-id'})

    def test_debug(self):
        """It expects a boolean value for the debug state."""
        config = use_config({'debug': True})
        assert config['debug']

        with pytest.raises(ConfigurationError):
            use_config({'debug': 1})

    def test_debug_default(self):
        """It defaults to disabled debug mode."""
        config = use_config()
        assert not config['debug']

    def test_database_default(self):
        """It defaults to an empty database dict."""
        config = use_config()
        assert config['database'] == {}

    def test_database_minimal(self):
        """It accepts minimal database information."""
        config = use_config({
            'database': {
                'engine': 'sqlite3',
                'name': 'test.sqlite3'
            }
        })

        assert config['database']['engine'] == 'sqlite3'
        assert config['database']['name'] == 'test.sqlite3'

    def test_database_full(self):
        """It accepts a full database configuration."""
        config = use_config({
            'database': {
                'engine': 'postgresql',
                'host': 'localhost',
                'name': 'test',
                'password': 'secret',
                'port': 1234,
                'user': 'test'
            }
        })

        assert config['database']['name'] == 'test'

    def test_database_validation(self):
        """It expects non-empty strings for all non-port parameters."""
        for param in ['engine', 'host', 'name', 'password', 'user']:
            config = use_config({'database': {param: 'valid'}})
            assert config['database'][param] == 'valid'

            with pytest.raises(ConfigurationError):
                use_config({'database': {param: ''}})

    def test_database_port(self):
        """It expects a numeric database port."""
        config = use_config({'database': {'port': 1234}})
        assert config['database']['port'] == 1234

        with pytest.raises(ConfigurationError):
            use_config({'database': {'port': '1234'}})

    def test_secret_key(self):
        """It expects a non-empty string for the secret key."""
        config = use_config({'secret_key': 'secret'})
        assert config['secret_key'] == 'secret'

        with pytest.raises(ConfigurationError):
            use_config({'secret_key': ''})

    def test_secret_key_default(self):
        """It defaults to a null value for the secret key."""
        config = use_config()
        assert config['secret_key'] is None

    def test_shopstyle_uid(self):
        """It expects a non-empty string for the Shopstyle UID."""
        config = use_config({'shopstyle_uid': 'uid'})
        assert config['shopstyle_uid'] == 'uid'

        with pytest.raises(ConfigurationError):
            use_config({'shopstyle_uid': None})

    def test_static_root(self):
        """It expects a non-empty string for the static root."""
        config = use_config({'static_root': '/tmp'})
        assert config['static_root'] == '/tmp'

        with pytest.raises(ConfigurationError):
            use_config({'static_root': ''})

    def test_static_root_absolute(self):
        """It expects an absolute path for the static root."""
        config = use_config({'static_root': '/tmp/dir'})
        assert config['static_root'] == '/tmp/dir'

        with pytest.raises(ConfigurationError):
            use_config({'static_root': 'tmp/dir'})

    def test_static_url(self):
        """It expects a non-empty string for the static URL."""
        config = use_config({'static_url': '/assets/'})
        assert config['static_url'] == '/assets/'

        with pytest.raises(ConfigurationError):
            use_config({'static_url': ''})

    def test_static_url_trailing_slash(self):
        """It expects the static URL to use a trailing slash."""
        config = use_config({'static_url': '/assets/'})
        assert config['static_url'] == '/assets/'

        with pytest.raises(ConfigurationError):
            use_config({'static_url': '/assets'})

    def test_static_url_root_path(self):
        """It allows a static URL to be the root path."""
        config = use_config({'static_url': '/'})
        assert config['static_url'] == '/'

    def test_static_url_absolute_url(self):
        """It allows a static URL to be an absolute URL."""
        config = use_config({'static_url': 'http://example.com/'})
        assert config['static_url'] == 'http://example.com/'
