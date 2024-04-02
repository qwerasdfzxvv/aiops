import logging
import time

logger = logging.getLogger(__name__)


def resubscribe(complete):
    """

    """
    pass

def retry(complete):
    logger.info('Retry params: {}'.format(complete))
    times = 0
    while True:
        try:
            resubscribe(complete)
            break
        except Exception as e:
            logger.error('Retry #{} {}  error: {}'.format(times, complete, e))
            times += 1
            time.sleep(times * 2)
