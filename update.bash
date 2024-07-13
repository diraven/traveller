#!/bin/bash
uv pip compile --all-extras pyproject.toml > requirements.txt
pre-commit autoupdate
