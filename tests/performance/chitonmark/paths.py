import os

# The absolute path to the directory containing benchmarks
BENCHMARKS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'benchmarks')

# The absolute path to the directory containing chitonmark
CHITONMARK_CONTAINER_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

# The absolute path to the directory for generated performance tests
TESTS_DIR = os.path.join(CHITONMARK_CONTAINER_DIR, 'tests')

# The absolute path to the root directory
ROOT_DIR = os.path.normpath(os.path.join(CHITONMARK_CONTAINER_DIR, '..', '..'))
