"""Performs devops test action."""
import glob

import subprocess
import click


@click.command()
@click.option('--migrations/--no-migrations', hidden=True, default=False)
def test(migrations: bool):
    """Performs full CI testing."""
    tests = sorted(glob.glob('devops/ci/tests/*'))

    with click.progressbar(tests) as bar:
        for test_item in bar:
            if migrations or 'migrations' not in test_item:
                completed_process = subprocess.run(
                    [
                        'bash',
                        test_item,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                if completed_process.returncode != 0:
                    click.secho('\n')
                    click.secho(test_item, fg='blue')
                    click.secho(completed_process.stdout.decode())
                    click.secho('FAIL', fg='red')
                    exit(1)

    click.secho('OK', fg='green')
