"""Handler that calls a binary executable on AWS lambda."""


import io
import json
import logging
import os
from subprocess import run, CalledProcessError
import sys
import tarfile
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
    extract_input(event)
    # Set up executable and shared library path
    LOG.info('event=%s', event)
    mybin = os.path.join(os.path.dirname(__file__), 'bin', 'jules.exe')
    try:
        run([mybin], check=True)
    except CalledProcessError as exc:
        LOG.exception(exc)
        raise
    else:
        return {
            'statusCode': 200,
            'body': get_output(),
            'headers': {'content-type': 'application/octet-stream'},
            'isBase64Encoded': True,
        }
    finally:
        tempdir.cleanup()
        os.chdir(oldcwd)


def main():
    """CLI for testing."""
    event = None
    if sys.argv[1:]:
        event = json.loads(sys.argv[1])
    handler(event, None)


def extract_input(event):
    """Get input from payload. Assume content is a tar(-gzip) archive."""
    with tarfile.open(fileobj=io.BytesIO(event['body'].encode())) as handle:
        handle.extractall()


def get_output():
    """Read output, turning it into a string containing a tar-gzip archive."""
    ret = io.BytesIO()
    with tarfile.open(fileobj=ret, mode='w:gz') as handle:
        for name in os.listdir('output'):
            handle.add(os.path.join('output', name), name)
    return ret


if __name__ == '__main__':
    main()
