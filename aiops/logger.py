import logging
import threading
import time
import copy
import random
import requests


class Demo:

    def __init__(self):
        self.logger = None

    def do_in_thread(self, i):
        try:
            self.logger.info('start--{}'.format(i))
            response = requests.get().json()
            self.logger.info(response)
        except Exception as ex:
            self.logger.error(ex)

    def run(self, i):
        setattr(self, 'CHGNAME', i)
        self.logger = logging.getLogger(name=i)
        handler = logging.FileHandler(filename='thread-demo-%s' % i)
        handler.setFormatter(
            logging.Formatter(" %(asctime)s %(levelname)s %(threadName)s %(thread)d %(ORDER_ID)s %(message)s"))

        class ContextFilter(logging.Filter):
            def filter(self, record):
                record.ORDER_ID = i
                return True

        self.logger.addFilter(ContextFilter())
        self.logger.addHandler(handler)

        times = 1
        while times < 10:
            time.sleep(random.randint(1, 3))
            self.logger.info('run--{}'.format(i))
            for x in range(3):
                threading.Thread(
                    target=self.do_in_thread,
                    args=(i + '-' + str(x),)
                ).start()
            times += 1
