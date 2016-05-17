#!/bin/bash

SCRIPTS_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
cd "$SCRIPTS_DIR" || exit

echo "Testing"
echo "-------"
./test.sh

echo
echo "Linting"
echo "-------"
./lint.sh
