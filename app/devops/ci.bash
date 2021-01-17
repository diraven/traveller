#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

black --check /app/
pylint /app/
cd .. && mypy -p app && cd app
