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
