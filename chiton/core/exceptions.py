class ConfigurationError(Exception):
    """An error indicating improper configuration."""


class FilesystemError(Exception):
    """An error indicating an issue with the filesystem."""


class FormatError(Exception):
    """An error indicating that the format of a data structure is invalid."""
