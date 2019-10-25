import logging


logging.basicConfig(
    datefmt='%Y%m%dT%H%M%S%z',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


def lambda_handler(event, context):
    LOG.info('event=%s', event)
    LOG.info('hello=world')
