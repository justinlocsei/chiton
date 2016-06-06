import json
import os
import re


def load_results(path):
    """Load benchmark results stored in a file.

    Args:
        path (str): The absolute path to the results file

    Returns:
        chitonmark.benchmark.BenchmarkResult: The loaded results
    """
    with open(path) as results_file:
        data = json.load(results_file)

    return BenchmarkResults(**data)


class BenchmarkResults:
    """The results of running a benchmark."""

    def __init__(self, calls=[], times=[]):
        """Create a new results instance.

        Keyword Args:
            calls (list[str]): Descriptions of function calls
            times (list[float]): Execution times for each run
        """
        self.calls = calls
        self.times = times

    def add_profile(self, profile):
        """Add the results of a cProfile session for the benchmark.

        Args:
            profile (str): The raw output of profiling
        """
        in_metrics = False
        for line in profile.split('\n'):
            if not in_metrics and 'ncalls' in line:
                in_metrics = True
                self.calls.append(line)
                continue
            elif not in_metrics:
                continue

            call = re.sub('\s%s.+site-packages' % os.sep, ' SITE', line)
            self.calls.append(call)

    def export(self, path):
        """Export the results to a file.

        Args:
            path (str): The absolute path to the target file
        """
        data = {
            'calls': self.calls,
            'times': self.times
        }

        with open(path, 'w') as results_file:
            json.dump(data, results_file)

    @property
    def average_time(self):
        """The average execution time for the benchmark.

        Returns:
            int: The execution time in milliseconds
        """
        return int((sum(self.times) / max(1, len(self.times))) * 1000)

    @property
    def runs(self):
        """The number of runs executed.

        Returns:
            int: The number of runs
        """
        return len(self.times)

    @property
    def total_time(self):
        """The total time spent.

        Returns:
            int: The total time in milliseconds
        """
        return int(sum(self.times) * 1000)
