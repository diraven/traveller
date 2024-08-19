#!/bin/bash
uv pip compile --all-extras pyproject.toml > requirements.txt
uv pip install -r requirements.txt
pre-commit autoupdate
