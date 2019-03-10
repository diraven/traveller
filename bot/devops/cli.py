"""Main command group."""

import click

MAX_LINE_LEN = 80


@click.group()
def cli():
    """Perform actions on the stack."""
