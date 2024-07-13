#!/bin/bash
uv pip compile pyproject.toml > requirements.txt
pre-commit autoupdate
