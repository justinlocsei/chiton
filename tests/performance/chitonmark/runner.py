import argparse
from importlib import import_module
import os
import subprocess
import shutil
import sys
import tempfile

from .paths import BENCHMARKS_DIR, ROOT_DIR
from .results import load_results
from .templates import create_pytest_file


def run():
    """Run benchmarks."""
    args = parse_args()
    run_benchmark(args.benchmark, calls=args.calls, source_only=args.source_only)


def parse_args():
    """Parse the command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    benchmark_files = [path for path in os.listdir(BENCHMARKS_DIR) if '__' not in path]
    benchmarks = sorted([file.replace('.py', '') for file in benchmark_files])

    parser = argparse.ArgumentParser(description='Run a bechmark')
    parser.add_argument('benchmark', metavar='BENCHMARK', choices=benchmarks, help='The benchmark to run')
    parser.add_argument('--calls', default=False, action='store_true', help='Whether to show call metrics')
    parser.add_argument('--source-only', default=False, action='store_true', help='Hide non-source calls')
    return parser.parse_args()


def run_benchmark(module_name, calls=False, source_only=False):
    """Run a single benchmark.

    Args:
        module_name (str): A benchmark module name

    Keyword Args:
        calls (bool): Whether to show call metrics
        source_only (bool): Whether to only show source calls
    """
    term_size = shutil.get_terminal_size((80, 20))
    divider = '-' * term_size.columns

    module = import_module('chitonmark.benchmarks.%s' % module_name)
    Benchmark = module.Benchmark

    results_file_fd, results_file_path = tempfile.mkstemp(suffix='.json')
    pytest_file_path = create_pytest_file(module_name, results_file_path, fixtures=Benchmark.fixtures)

    print(divider)
    print('Test Run')
    print(divider)
    pytest = subprocess.Popen(['py.test', pytest_file_path])

    try:
        pytest.wait()
    except KeyboardInterrupt:
        pytest.terminate()
        sys.exit(1)
    else:
        results = load_results(results_file_path)
    finally:
        os.remove(pytest_file_path)
        os.close(results_file_fd)
        os.remove(results_file_path)

    print()

    if calls:
        print(divider)
        print('Calls')
        print(divider)
        for call in results.calls:
            if source_only and ROOT_DIR not in call:
                continue
            elif source_only:
                call = call.replace('%s%s' % (ROOT_DIR, os.path.sep), '')
            print(call)

    print(divider)
    print('Summary')
    print(divider)
    print('Benchmark:    %s' % module_name)
    print('Runs:         %d' % results.runs)
    print('Total time:   %dms' % results.total_time)
    print('Average time: %dms\n' % results.average_time)


if __name__ == '__main__':
    run()
