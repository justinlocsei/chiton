#!/bin/bash

REPO_ROOT="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
PERF_DIR="$REPO_ROOT/tests/performance"
cd "$REPO_ROOT" && PYTHONPATH="$PERF_DIR" python -m chitonmark.runner "$@"
