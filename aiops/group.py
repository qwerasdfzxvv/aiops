from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import requests
import inspect
import logging
import time
import random
from operator import itemgetter
from itertools import groupby

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(levelname)s] [ %(filename)s:%(lineno)s - %(name)s ] %(message)s')


class NginfFile:
    actions = [
        {'action_name': '步骤1', 'action_func': 'stop_m'},
        {'action_name': '步骤2', 'action_func': 'rung_backup'},
        {'action_name': '步骤3', 'action_func': 'query'},
        {'action_name': '步骤4', 'action_func': 'deploy'},
        {'action_name': '步骤5', 'action_func': 'query'},
        {'action_name': '步骤6', 'action_func': 'start_m'},
    ]

    def __init__(self):
        self.queues = [
            {'queue_id': 'a', 'region': 'x'},
            {'queue_id': 'b', 'region': 'x'},
            {'queue_id': 'c', 'region': 'x'},
            {'queue_id': 'd', 'region': 'y'},
            {'queue_id': 'e', 'region': 'y'},
            {'queue_id': 'f', 'region': 'y'},
        ]
        self.session = self.create_session()

        self.is_group = False

    def create_session(self):
        session = requests.session()
        return session

    def get_data(self, method, url, **kwargs):
        return self.session.request(method=method, url=url, **kwargs).json()

    def parse_params(self, queue, action):
        params = {
            'stop_m': {'queue_id': queue['queue_id']},
            'rung_backup': {'queue_id': queue['queue_id']},
            'query': {'queue_id': queue['queue_id']},
            'deploy': {'queue_id': queue['queue_id']},
            'start_m': {'queue_id': queue['queue_id']},
        }
        return params[action]

    def sort_group(self):
        self.queues.sort(key=itemgetter('region'))
        queues = groupby(self.queues, itemgetter('region'))
        group_data = []

        for region, group in queues:
            group_data.append({'group': region, 'data': [q for q in group]})
        self.queues = group_data

    def run_async(self, action, queues):

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            ok = []
            bad = []
            futures = {
                executor.submit(
                    getattr(self, action['action_func']),
                    self.parse_params(queue, action['action_func'])
                ): action['action_name']
                for queue in queues
            }
            logger.info('开始执行步骤：%s', action['action_name'])
            for future in concurrent.futures.as_completed(futures):
                future_action = futures[future]
                try:
                    future_data = future.result()
                    if future_data:
                        ok.append(future_data)
                    else:
                        bad.append(future_data)
                except Exception as exc:
                    bad.append({'error': exc, **future_action})
                    logger.exception(exc)
                    logger.error('%s 执行报错:%s', future_action, exc)

            return {'ok': ok, 'bad': bad}

    def run(self):

        if not self.queues:
            logger.info('不涉及')
            return
        if self.is_group:
            self.sort_group()
            for group_queues in self.queues:
                logger.info('开始处理机房：%s', group_queues['group'])
                for action in self.actions:
                    action_result = self.run_async(action, group_queues['data'])
                    logger.info('运行结果:%s', action_result)
                    if action_result['bad']:
                        logger.error('%s,%s', action, action_result['bad'])
                        break
                else:
                    continue
                break
        else:
            for action in self.actions:
                action_result = self.run_async(action, self.queues)
                logger.info('运行结果:%s', action_result)
                if action_result['bad']:
                    logger.error('%s,%s', action, action_result['bad'])
                    break

    def stop_m(self, queue_id):
        logger.info('运行%s,queue_id=%s', inspect.stack()[0][3], queue_id)
        time.sleep(random.randint(0, 3))
        return random.choice([True, True])

    def rung_backup(self, queue_id):
        logger.info('运行%s,queue_id=%s', inspect.stack()[0][3], queue_id)
        time.sleep(random.randint(0, 3))
        return random.choice([True, True, True, True, True, True, True, True, True])

    def query(self, queue_id):
        logger.info('运行%s,queue_id=%s', inspect.stack()[0][3], queue_id)
        time.sleep(random.randint(0, 3))
        return random.choice([True, False])

    def deploy(self, queue_id):
        logger.info('运行%s,queue_id=%s', inspect.stack()[0][3], queue_id)
        time.sleep(random.randint(0, 3))
        return random.choice([True, True])

    def start_m(self, queue_id):
        logger.info('运行%s,queue_id=%s', inspect.stack()[0][3], queue_id)
        time.sleep(random.randint(0, 3))
        return random.choice([True, True])


if __name__ == '__main__':
    NginfFile().run()
