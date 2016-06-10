import os

from .paths import TESTS_DIR


def create_pytest_file(module_name, results_path, fixtures=[], runs=100):
    """Create a pytest file to run the benchmark.

    Args:
        module_name (str): The name of the benchmark's module
        results_path (str): The absolute path to the file that will contain the results

    Keyword Args:
        fixtures (list[str]): The names of all pytest fixtures to use
        runs (int): The number of test runs to perform

    Returns:
        str: The absolute path to the runner file
    """
    fixtures = sorted(fixtures)

    fixtures_dict = ['{']
    for fixture in fixtures:
        fixtures_dict.append("'%s': %s," % (fixture, fixture))
    fixtures_dict.append('}')
    fixtures_dict = ''.join(fixtures_dict)

    if fixtures:
        fixtures_signature = ', %s' % ', '.join(fixtures)
    else:
        fixtures_signature = ''

    pytest_code = """
import cProfile
import io
import json
import pstats
from time import time as get_time

from django.db import IntegrityError, transaction
import pytest

from chitonmark.benchmarks.%(module_name)s import Benchmark
from chitonmark.results import BenchmarkResults


class TestBenchmark:

    @pytest.mark.django_db(transaction=True)
    def test_performance(self%(fixtures_signature)s):
        fixtures = %(fixtures_dict)s

        benchmark = Benchmark()
        benchmark.pre_run(fixtures)
        benchmark.log('--')

        result = BenchmarkResults()
        profile = cProfile.Profile()

        for run in range(0, %(runs)d):
            try:
                with transaction.atomic():
                    start_time = get_time()
                    profile.enable()

                    benchmark.run(fixtures)

                    profile.disable()
                    end_time = get_time()

                    run_time = end_time - start_time
                    result.times.append(run_time)
                    benchmark.log('Run %%d / %%d: %%dms' %% (run + 1, %(runs)d, run_time * 1000))

                    raise IntegrityError()
            except IntegrityError:
                pass

        stats_data = io.StringIO()
        stats = pstats.Stats(profile, stream=stats_data).sort_stats('cumulative').reverse_order()
        stats.print_stats()
        result.add_profile(stats_data.getvalue())

        benchmark.post_run()

        result.export('%(results_path)s')
    """ % {
        'fixtures_dict': fixtures_dict,
        'fixtures_signature': fixtures_signature,
        'module_name': module_name,
        'results_path': results_path,
        'runs': runs
    }

    pytest_file_path = os.path.join(TESTS_DIR, 'test_%s.py' % module_name)
    with open(pytest_file_path, 'w') as pytest_file:
        pytest_file.write(pytest_code.strip())
        pytest_file.close()

    return pytest_file_path
