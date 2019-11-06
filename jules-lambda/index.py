"""Handler that calls a binary executable on AWS lambda."""


import json
import logging
import os
from pathlib import Path
from shutil import copytree, copy2
from subprocess import run, CalledProcessError
import sys
from tempfile import TemporaryDirectory


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


def handler(event, context):
    """Handle the lambda call."""
    # Run in a temporary location to guarantee writable
    tempdir = TemporaryDirectory()
    oldcwd = os.getcwd()
    os.chdir(tempdir.name)
    os.makedirs('output')
    pull_input()
    # Set up executable and shared library path
    LOG.info('event=%s', event)
    mybindir = Path(__file__).parent
    mybin = mybindir.joinpath('bin/jules.exe')
    try:
        proc = run([str(mybin)], check=True)
    except CalledProcessError as exc:
        LOG.exception(exc)
        raise
    else:
        put_output()
    finally:
        tempdir.cleanup()
        os.chdir(oldcwd)


def main():
    """CLI for testing."""
    event = None
    if sys.argv[1:]:
        event = json.loads(sys.argv[1])
    handler(event, None)


def pull_input():
    """Get input from source, assuming that the source is a zip file.

    Source location hard coded for now.
    It will become an item location in an S3 bucket.
    """
    for name in os.listdir('/var/task/data'):
        copy2(os.path.join('/var/task/data', name), '.')


def put_output():
    """Copy items in output directory to destination.

    Destination location hard coded for now.
    It will become an item location in an S3 bucket.
    """
    try:
        copytree('./output', '/var/task/output')
    except OSError as exc:
        # Ignore error for now
        LOG.exception(exc)


if __name__ == '__main__':
    main()
