#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

# Enforce code style.
black --check crabot

# Enforce code style.
bandit --configfile bandit.yml --recursive crabot

# Run linting.
pylint crabot

# Run typing.
mypy crabot

# Run tests.
python3 -m pytest
