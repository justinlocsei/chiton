import re


# A regex to find all path separators
PATH_SEPARATOR_SEARCH = re.compile(r'[/\\]')

# A regex to remove duplicate URL separators
URL_SEPARATOR_SEARCH = re.compile(r'([^:])/{2,}')


def file_path_to_relative_url(path):
    """Convert a file path to a relative URL.

    Args:
        path (str): A relative file path

    Returns:
        str: The path as a URL
    """
    return re.sub(PATH_SEPARATOR_SEARCH, '/', path)


def join_url(*parts):
    """Join the components of a URL.

    Args:
        paths (list[str]): The URLs components

    Returns:
        str: The joined URL
    """
    joined = '/'.join(parts)
    return re.sub(URL_SEPARATOR_SEARCH, r'\1/', joined)
