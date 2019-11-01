"""Handler that calls a binary executable on AWS lambda."""


import json
import logging
from pathlib import Path
from subprocess import run, CalledProcessError
import sys


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


def handler(event, context):
    """Handle the lambda call. "event" contains the payload."""
    LOG.info('event=%s', event)
    mybindir = Path(__file__).parent
    mybin = mybindir.joinpath('index.bin')
    try:
        proc = run(
            [str(mybin)], capture_output=True, check=True, cwd=str(mybindir))
    except CalledProcessError as exc:
        log_proc(mybin, exc)
        LOG.exception(exc)
        raise
    else:
        log_proc(mybin, proc)


def log_proc(mybin, proc):
    """Log the stdout/stderr from proc."""
    if proc.stderr:
        LOG.error('%s says "%s"', mybin, proc.stderr)
    if proc.stdout:
        LOG.info('%s says "%s"', mybin, proc.stdout)


def main():
    """CLI for testing."""
    event = None
    if sys.argv[1:]:
        event = json.loads(sys.argv[1])
    handler(event, None)


if __name__ == '__main__':
    main()
