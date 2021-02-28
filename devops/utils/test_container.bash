#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
set -o xtrace
bash devops/utils/echo_info.bash "Test $(pwd)"

# Enforce code style.
black --check .

# Enforce code style.
bandit --configfile devops/configs/bandit.yml --recursive .

# Run linting.
find . -type f -name "*.py" -not -path '*/\.*' | xargs pylint --rcfile devops/configs/.pylintrc

# Run typing.
mypy --config-file devops/configs/mypy.ini .

# Run tests.
cp devops/configs/pytest.ini .
pytest
