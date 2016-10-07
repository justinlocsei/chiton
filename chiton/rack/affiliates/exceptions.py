class LookupError(Exception):
    """An error indicating an issue with an item lookup."""


class ConfigurationError(Exception):
    """An internal error raised when expected formats are not followed."""


class ThrottlingError(Exception):
    """An internal error raised when an API throttles a request."""


class BatchError(Exception):
    """An error raised when a batch of jobs fails."""
