class BaseBenchmark:
    """The base class for all benchmarks."""

    fixtures = []

    def __init__(self):
        """Create a new benchmark."""
        self.imports = self.resolve_imports()

    def resolve_imports(self):
        """Allow a benchmark to resolve its imports.

        Returns:
            dict: A mapping between names and imported objects
        """
        return {}

    def log(self, message, update=False):
        """Log a message.

        Args:
            message (str): The text of the message

        Keyword Args:
            update (bool): Whether to update the line in-place
        """
        if update:
            print('%s\r' % message, end="")
        else:
            print(message)

    def pre_run(self, fixtures):
        """Allow the benchmark to perform pre-run setup.

        Args:
            fixtures (dict): A mapping of fixture names to instances
        """
        pass

    def post_run(self):
        """Allow the benchmark to perform post-run teardown."""
        pass

    def run(self, fixtures):
        """Allow the benchmark to provide its code.

        Args:
            fixtures (dict): A mapping of fixture names to instances
        """
        raise NotImplementedError()
