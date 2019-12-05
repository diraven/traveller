pwd=$(shell pwd)
SHELL=/bin/bash -o errexit -o pipefail -o nounset

ci: static_analysis type_checking

cd:
	@docker-compose build
	@docker-compose push

run:
	@docker-compose up -d

static_analysis: run
	@docker-compose run --rm app flake8 /app | sed -e "s|^/app|$(pwd)/app|"

type_checking: run
	@docker-compose run --rm app mypy /app | sed -e "s|^|$(pwd)/app/|"

frozen_requirements:
	@python -m venv .tmpvenv
	@.tmpvenv/bin/pip install -U pip setuptools
	@.tmpvenv/bin/pip install --no-cache-dir --requirement app/requirements.txt
	@.tmpvenv/bin/pip freeze > app/requirements.frozen.txt
	@rm -rf .tmpvenv
