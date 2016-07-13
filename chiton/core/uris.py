import re


# A regex to find all path separators
PATH_SEPARATOR_SEARCH = re.compile(r'[/\\]')


def file_path_to_relative_url(path):
    """Convert a file path to a relative URL.

    Args:
        path (str): A relative file path

    Returns:
        str: The path as a URL
    """
    return re.sub(PATH_SEPARATOR_SEARCH, '/', path)
