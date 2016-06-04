import cProfile
import io
import pstats
import re
from time import time as get_time


class Benchmark:
    """The base class for all benchmarks."""

    def pre_run(self):
        """Allow the benchmark to perform pre-run setup."""
        pass

    def post_run(self):
        """Allow the benchmark to perform post-run teardown."""
        pass

    def profile(self, runs=100):
        """Profile the execution of the benchmark's code.

        Args:
            runs (int): The number of benchmark runs

        Returns:
            BenchmarkResult: The result of the benchmark
        """
        result = BenchmarkResult()

        self.pre_run()
        profile = cProfile.Profile()

        for run in range(0, runs):
            start_time = get_time()
            profile.enable()
            self.run()
            profile.disable()
            end_time = get_time()

            result.record_time(end_time - start_time)

        self.post_run()

        stats_data = io.StringIO()
        stats = pstats.Stats(profile, stream=stats_data).sort_stats('cumulative')
        stats.print_stats()

        result.add_profile(stats_data.getvalue())

        return result

    def run(self):
        """Allow the benchmark to provide its code."""
        raise NotImplementedError()


class BenchmarkResult:
    """A result of running a benchmark."""

    def __init__(self):
        """Create a new benchmark result."""
        self.calls = []
        self._times = []

    def record_time(self, time):
        """Record an execution time for the benchmark.

        Args:
            time (float): The execution time in seconds
        """
        self._times.append(time)

    def add_profile(self, profile):
        """Add the results of a cProfile session for the benchmark.

        Args:
            caller (str): The raw output of profiling
        """
        in_metrics = False
        for line in profile.split('\n'):
            if not in_metrics and 'ncalls' in line:
                in_metrics = True
                continue
            elif not in_metrics:
                continue
            elif "method 'disable'" in line:
                continue

            parts = re.split(r'\s+', line.strip())
            if len(parts) < 2:
                continue

            self.calls.append({
                'line': ' '.join(parts[5:]),
                'total': int(parts[0]),
                'time': float(parts[1]) * 1000
            })

    @property
    def average_time(self):
        """The average execution time for the benchmark.

        Returns:
            int: The execution time in milliseconds
        """
        return int((sum(self._times) / max(1, len(self._times))) * 1000)

    @property
    def runs(self):
        """The number of runs executed.

        Returns:
            int: The number of runs
        """
        return len(self._times)

    @property
    def total_time(self):
        """The total time spent.

        Returns:
            int: The total time in milliseconds
        """
        return int(sum(self._times) * 1000)
