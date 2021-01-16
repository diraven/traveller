#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

black --check /workspace/app/
pylint /workspace/app/
mypy -p app
