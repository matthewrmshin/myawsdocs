from contextlib import suppress
import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
FILENAME_WHO_NL = 'who.nl'


def lambda_handler(event, context):
    """Handle the lambda call. "event" contains the payload."""
    LOG.info('event=%s', event)
    if event and event.get('who'):
        tempd = TemporaryDirectory()
        oldcwd = os.getcwd()
        os.chdir(tempd.name)
        with open(FILENAME_WHO_NL, 'w') as handle:
            handle.write('&who_nl who="%(who)s", /\n' % event)
            handle.close()
        try:
            invoke_hello(event, context)
        finally:
            os.chdir(oldcwd)
    else:
        invoke_hello(event, context)


def invoke_hello(event, context):
    """Invoke the "hello.bin" program."""
    mybin = Path(__file__).parent.joinpath('hello.bin')
    proc = Popen([str(mybin)], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    if err:
        LOG.error('%s says "%s"', mybin, err)
    if out:
        LOG.info('%s says "%s"', mybin, out)
    if proc.wait():
        exc = RuntimeError('%s returns %d' % (mybin, proc.returncode))
        LOG.exception(exc)
        raise exc


if __name__ == '__main__':
    import json
    import sys
    arg1 = None
    if sys.argv[1:]:
        arg1 = json.loads(sys.argv[1])
    lambda_handler(arg1, None)
