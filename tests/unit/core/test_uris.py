from chiton.core.uris import extract_query_param, file_path_to_relative_url, join_url


class TestExtractQueryParam:

    def test_missing(self):
        """It returns None when a param is missing."""
        assert extract_query_param('http://example.com', 'id') is None

    def test_single(self):
        """It returns the param as a list when it is present."""
        assert extract_query_param('http://example.com?id=1', 'id') == ['1']

    def test_multiple(self):
        """It returns all values for the value."""
        assert extract_query_param('http://example.com?id=1&id=2', 'id') == ['1', '2']


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


class TestJoinUrl:

    def test_single(self):
        """It returns a flat path without modifications."""
        assert join_url('file.txt') == 'file.txt'

    def test_relative(self):
        """It joins components with a URL path separator."""
        assert join_url('relative', 'file.txt') == 'relative/file.txt'

    def test_relative_nested(self):
        """It respects existing separators."""
        assert join_url('relative/path', 'to/file.txt') == 'relative/path/to/file.txt'

    def test_relative_root(self):
        """It respects a rooted relative path."""
        assert join_url('/absolute', 'file.txt') == '/absolute/file.txt'

    def test_trim(self):
        """It trims excess slashes."""
        assert join_url('one/', '/two/', '/three//', 'four.txt') == 'one/two/three/four.txt'

    def test_trailing_slash(self):
        """It respects trailing slashes."""
        assert join_url('dir', 'path') == 'dir/path'
        assert join_url('dir', 'path/') == 'dir/path/'
        assert join_url('dir', 'path//') == 'dir/path/'

    def test_absolute(self):
        """It respects absolute URLs."""
        assert join_url('http://example.com', 'one', 'two') == 'http://example.com/one/two'

    def test_absolute_slashes(self):
        """It applies normal slash-trimming rules to absolute URLs."""
        assert join_url('http://example.com/', '/file.txt') == 'http://example.com/file.txt'

    def test_root_relative(self):
        """It does not trim root-relative URLs."""
        assert join_url('//example.com', 'file.txt') == '//example.com/file.txt'
