#!/bin/bash
uv pip compile --all-extras pyproject.toml > requirements.txt
uv pip instal -r requirements.txt
pre-commit autoupdate
