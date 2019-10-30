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
    mybin = Path(__file__).parent.joinpath('index.bin')
    try:
        proc = run([str(mybin)], capture_output=True, check=True)
    except CalledProcessError as exc:
        LOG.exception(exc)
        raise
    else:
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
