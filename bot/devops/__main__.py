"""Performs operations on app stack."""

from cli import cli
from test import test

cli.add_command(test)

if __name__ == '__main__':
    cli()
