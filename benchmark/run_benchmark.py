#!/usr/bin/env python

import argparse
import glob
from importlib import import_module
import inspect
import os
from pathlib import PurePath
import sys


# The absolute path to the directory containing benchmarks
BENCHMARKS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'benchmarks')


def run():
    """Run benchmarks."""
    args = parse_args()
    benchmarks = resolve_benchmark_module_paths(args.benchmark)

    configure_environment()
    for benchmark in benchmarks:
        run_benchmark_module(benchmark)


def configure_environment():
    """Allow benchmarks to be imported as modules."""
    sys.path.append(os.path.dirname(BENCHMARKS_DIR))


def parse_args():
    """Parse the command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(description='Run bechmarks')
    parser.add_argument('benchmark', metavar='BENCHMARK', nargs='*', default=[BENCHMARKS_DIR], help='Benchmark files to run')
    return parser.parse_args()


def resolve_benchmark_module_paths(globs):
    """Convert a list of benchmark paths to module paths.

    Args:
        globs (list[str]): Globs of benchmarks to run

    Returns:
        list[str]: Paths to importable benchmark modules
    """
    expanded = set()
    for benchmark in globs:
        if os.path.isdir(benchmark):
            expanded.add(os.path.join(benchmark, '*'))
        else:
            expanded.add(benchmark)

    normalized = set()
    for benchmark in expanded:
        for file in glob.glob(benchmark, recursive=True):
            normalized.add(os.path.realpath(file))

    ordered = sorted(list(normalized))
    full_paths = [PurePath(path) for path in ordered if '__' not in path]
    relative_paths = [str(path.relative_to(BENCHMARKS_DIR)) for path in full_paths]
    module_paths = [
        '%s.%s' % (os.path.basename(BENCHMARKS_DIR), path.replace(os.path.sep, '.').replace('.py', ''))
        for path in relative_paths
    ]

    return module_paths


def run_benchmark_module(module_path):
    """Run a single benchmark.

    Args:
        module_path (str): A benchmark module path
    """
    from benchmarks import Benchmark

    benchmarks = []
    for name, obj in inspect.getmembers(import_module(module_path)):
        try:
            if obj is not Benchmark and issubclass(obj, Benchmark):
                benchmarks.append((name, obj))
        except TypeError:
            pass

    for benchmark in sorted(benchmarks, key=lambda b: b[0]):
        run_benchmark(benchmark[0], benchmark[1]())


def run_benchmark(name, benchmark):
    """Run a single benchmark.

    Args:
        name (str): The name of the benchmark
        benchmark (Benchmark): A benchmark instance
    """
    result = benchmark.profile()

    print('%s\n%s' % (name, '-' * len(name)))
    print('Runs: %d' % result.runs)
    print('Total time: %dms' % result.total_time)
    print('Average time: %dms\n' % result.average_time)

    for call in result.calls:
        print('%d (%dms) %s' % (call['total'], call['time'], call['line']))

    print()


if __name__ == '__main__':
    run()
