import time
from enum import Enum
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

logger = logging.getLogger(__name__)


class Action(Enum):
    """
    工单状态
    """

    do_action_closed = 'do_action_closed'
    do_action_upgrade = 'do_action_upgrade'
    do_action_maximum = 'do_action_maximum'
    do_action_normal = 'do_action_normal'

    @classmethod
    def do_action_normal_format(cls, **kwargs):
        return '【第{num}次巡检{msg}】{detail}'.format(**kwargs)


class WriteBackMixin:
    """
    数据写入类
    """

    upgrade_name = '未恢复'
    upgrade_threshold = 5

    maximum_threshold = 10

    closed_threshold = 3
    closed_name = '已恢复'

    term_id = ('1', '2', '3',)

    def __init__(self):
        self.alters_map = {}
        self.url = 'https://mock.presstime.cn/mock/6607f5193d7acdc52db6fe3f/example/mock'

    def do_action_upgrade(self, lst_data, **kwargs):
        """
        判断是否需要升级工单
        :param lst_data: 列表数据
        :return:
        """
        if len(lst_data) < self.upgrade_threshold:
            return
        latest_data = lst_data[-self.upgrade_threshold:]
        logger.info(f'latest_data:{latest_data}')
        if any([self.upgrade_name not in i for i in latest_data]):
            return
        return {'action': Action.do_action_upgrade}

    def do_action_maximum(self, lst_data, **kwargs):
        """
        判断是否已达最大写入次数
        :param lst_data: 列表数据
        :return:
        """
        if len(lst_data) < self.maximum_threshold:
            return
        return {'action': Action.do_action_maximum}

    def do_action_closed(self, lst_data, **kwargs):
        """
        判断是否需要关闭工单
        :param lst_data: 列表数据
        :return:
        """
        if len(lst_data) < self.closed_threshold:
            return
        latest_data = lst_data[-self.closed_threshold:]
        logger.info(f'latest_data:{latest_data}')
        if any([self.closed_name not in i for i in latest_data]):
            return
        return {'action': Action.do_action_closed}

    def do_action_normal(self, lst_data, **kwargs):
        """
        判断是否需要恢复正常
        :param lst_data: 列表数据
        :return:
        """
        result = self.evaluate(alter_key=kwargs.get('alter_key'))
        return {
            'num': len(lst_data) + 1,
            'action': Action.do_action_normal,
            **result}

    def evaluate(self, **kwargs) -> dict:
        return {'msg': '恢复正常', 'detail': '相关阀值数据为100'}

    def do_update(self, **kwargs):
        alter_key = kwargs.get('alter_key')
        alter_time = self.alters_map.get(alter_key).get('time')
        action = kwargs.get('action')
        msg = ''
        if action == Action.do_action_closed:
            msg = Action.do_action_closed.value
        if action == Action.do_action_maximum:
            msg = Action.do_action_maximum.value
        if action == Action.do_action_upgrade:
            msg = Action.do_action_upgrade.value
        if action == Action.do_action_normal:
            msg = Action.do_action_normal_format(**kwargs)
        params = {
            'alter_key': alter_key,
            'time': alter_time,
            'msg': msg
        }
        logger.info(f'params:{params}')
        # try:
        #     requests.put(url=self.url, params=params).json()
        # except Exception as exc:
        #     logger.exception(exc)

    def load_alters_data(self, alter_source):
        """
        加载告警数据
        :param alter_source: 告警来源
        :return: None
        """
        logger.info(f"{self.__class__.__name__} load_alters_data")
        try:

            resp = requests.get(url=self.url, params={"alter_source": alter_source}).json()
        except Exception as exc:
            pass

        def gen_data():
            test_data = []
            for i in range(random.randint(2, 50)):
                tt=[]
                for x in range(random.randint(2, 12)):
                    tt.append({'user': 'rebot_txt', 'remark': '{}'.format(random.choice(['已恢复', '未恢复']))})
                dd={
                        "alter_key": "alter_key_"+str(i),
                        "term_id": "1",
                        "records": {'2024-04-12':tt}
                    }
                test_data.append(dd)
            return test_data

        resp = {
            "result": {
                "recordList": gen_data()
            }
        }

        data = []
        if resp.get('result', {}).get('data'):
            data.append(resp.get('result', {}).get('data'))
        if resp.get('result', {}).get('recordList'):
            data += resp.get('result', {}).get('recordList')
        for d in data:
            if d.get('term_id') not in self.term_id:
                continue
            self.alters_map[d.get('alter_key')] = d

    def do(self, alter_key):
        logger.info(f"{alter_key} do")
        # 告警内容
        alter_value = self.alters_map[alter_key]
        # 回写日志列表
        lst_data = []
        for _, records in alter_value['records'].items():
            for record in records:
                if 'rebot_txt' in record['user']:
                    lst_data.append(record['remark'])
        logger.info(f'{lst_data}')
        logger.info(f'{len(lst_data)}')

        for lst in lst_data:
            for _, member in Action.__members__.items():
                if member.value in lst:
                    logger.info(f'{alter_key} {member.value} in {lst}  now ignore')
                    return

        for fn_name, member in Action.__members__.items():
            action_fn = getattr(self, fn_name)
            resp = action_fn(lst_data=lst_data, alter_key=alter_key)
            logger.info(f'{fn_name} resp is {resp}')
            if resp:
                self.do_update(alter_key=alter_key, **resp)
                # 终止下一个步骤
                logger.info(f'=================================')
                return

    def run(self, alter_source, **kwargs):

        # 为对象设置属性值
        for k, v in kwargs.items():
            setattr(self, k, v)

        #  加载告警数据
        self.load_alters_data(alter_source)
        logger.info(len(self.alters_map.keys()))
        # 并发处理告警
        with ThreadPoolExecutor(max_workers=10, thread_name_prefix='do_action') as executor:
            futures = {
                executor.submit(self.do, alter_key): (alter_key,)
                for alter_key in self.alters_map.keys()
            }
            for future in as_completed(futures):
                alter_key = futures[future]
                logger.info(f'{alter_key} has done')
                try:
                    future.result()
                except Exception as exc:
                    logger.exception(exc)
                    print(f"获取{alter_key}数据并处理时发生错误: {exc}")

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(thread)d  -%(threadName)s -%(funcName)s  - %(levelname)s - %(message)s')
wb = WriteBackMixin()
# # wb.load_alters_data(alter_source='x')
wb.run(alter_source='x')
# # print(wb.alters_map)
