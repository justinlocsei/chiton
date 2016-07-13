import pytest

from chiton.core.uris import file_path_to_relative_url


@pytest.mark.current
class TestFilePathToRelativeUrl:

    def test_flat(self):
        """It returns a flat path without modifications."""
        assert file_path_to_relative_url('test.txt') == 'test.txt'

    def test_directories_unix(self):
        """It returns UNIX-style paths without modifications."""
        assert file_path_to_relative_url('/absolute/file.txt') == '/absolute/file.txt'
        assert file_path_to_relative_url('relative/file.txt') == 'relative/file.txt'

    def test_directories_windows(self):
        """It returns Windows-style paths as URLs."""
        assert file_path_to_relative_url(r'\absolute\file.txt') == '/absolute/file.txt'
        assert file_path_to_relative_url(r'relative\file.txt') == 'relative/file.txt'
