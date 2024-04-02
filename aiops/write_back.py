from threading import Thread
from enum import Enum
import requests
import logging

logger = logging.getLogger(__name__)


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

    class ExistStatus(Enum):
        """
        工单状态
        """
        UPGRADE = 'UPGRADE'
        MAXIMUM = 'MAXIMUM'
        CLOSED = 'CLOSED'
        NORMAL = 'NORMAL'

    def do_upgrade(self, lst_data, **kwargs):
        """
        判断是否需要升级工单
        :param lst_data: 列表数据
        :return: bool|None
        """
        for ld in lst_data:
            if self.ExistStatus.UPGRADE in ld:
                return
        if len(lst_data) > self.upgrade_threshold:
            latest_data = lst_data[-self.upgrade_threshold:]
            if all(self.upgrade_name in i for i in latest_data):
                return True

    def do_maximum(self, lst_data, **kwargs):
        """
        判断是否已达最大写入次数
        :param lst_data: 列表数据
        :return: bool|None
        """
        for ld in lst_data:
            if self.ExistStatus.MAXIMUM in ld:
                return
        if len(lst_data) > self.maximum_threshold:
            return True

    def do_closed(self, lst_data, **kwargs):
        """
        判断是否需要关闭工单
        :param lst_data: 列表数据
        :return: bool|None
        """
        for ld in lst_data:
            if self.ExistStatus.CLOSED in ld:
                return
        if len(lst_data) > self.closed_threshold:
            latest_data = lst_data[-self.closed_threshold:]
            if all(self.closed_name in i for i in latest_data):
                return True

    def do_normal(self, lst_data, **kwargs):
        """
        判断是否需要恢复正常
        :param lst_data: 列表数据
        :return: bool|None
        """
        alter_key = kwargs.get('alter_key')
        if not alter_key:
            return
        status=self.evalurate(alter_key=alter_key, **kwargs)
        if len(lst_data) > self.closed_threshold:
            latest_data = lst_data[-self.closed_threshold:]
            if all(self.closed_name in i for i in latest_data):
                return True

    def evalurate(self, alter_key, **kwargs):

        return True

    def load_alters_data(self, alter_source):
        """
        加载告警数据
        :param alter_source: 告警来源
        :return: None
        """
        resp = requests.get(url=self.url, params={"alter_source": alter_source}).json()

        resp = {
            "result": {

                "recordList": [
                    {
                        "alter_key": "alter_key_001",
                        "term_id": "1",
                        "records": {
                            '2024-04-12': [
                                {'user': 'rebot_txt', 'remart': 'rebot_01'},
                                {'user': 'unknow', 'remart': 'rebot_01'},
                                {'user': 'rebot_txt', 'remart': 'rebot_01'},
                                {'user': 'rebot_txt', 'remart': 'rebot_01'}
                            ],
                            '2024-04-13': [
                                {'user': 'rebot_txt', 'remart': 'rebot_02'},
                                {'user': 'unknow', 'remart': 'rebot_02'},
                                {'user': 'rebot_txt', 'remart': 'rebot_02'},
                                {'user': 'rebot_txt', 'remart': 'rebot_02'}
                            ]
                        }}

                ]
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

    def do_in_thread(self, handler, *args, **kwargs):
        logger.info(f"{handler.__name__}")
        data = self.initial_data
        try:
            response = handler(*args, **kwargs)
            data["status"] = "ok"
            data["resp"] = response
        except Exception as e:
            logger.exception(e)
            data["error"] = str(e)
            data["status"] = "error"

    def is_need_async(self):
        """
        判断是否需要异步执行
        """
        return True

    def do_async(self, handler, *args, **kwargs):
        """
        异步执行
        :param handler: 处理方法
        :param args:  参数
        :param kwargs: kv参数
        :return:
        """
        if handler.__name__ != 'do_normal':
            kwargs.pop('alter_key')
        t = Thread(
            target=self.do_in_thread,
            args=(handler, *args),
            kwargs=kwargs
        )
        t.start()
        # 可以做一些格式处理
        resp = self.initial_data
        return resp

    @property
    def initial_data(self):
        return {
            "status": "ok",
            "resp": None,
            "error": None
        }

    def async_callback(self, *args, **kwargs):
        logger.info(f"{self.__class__.__name__} async callback")
        logger.info((args, kwargs))
        # raise NotImplementedError()

    def do(self, handler, *args, **kwargs):
        if not self.is_need_async():
            return handler(*args, **kwargs)
        resp = self.do_async(handler, *args, **kwargs)
        self.async_callback(*args, **kwargs)
        return resp

    def run(self, alter_source, **kwargs):

        # 为对象设置属性值
        for k, v in kwargs.items():
            setattr(self, k, v)

        try:
            #  加载告警数据
            self.load_alters_data(alter_source)

            for alter_key, alter_value in self.alters_map.items():
                # 筛选出包含rebot_txt键的记录
                lst_data = []
                for _, records in alter_value['records'].items():
                    for record in records:
                        if 'rebot_txt' in record['user']:
                            lst_data.append(record['remart'])
                print(lst_data)
                # records = [v for _, v in alter_value['records'].items() if 'rebot_txt' in v['user']]
                



                for step in ['do_normal', 'do_closed', 'do_upgrade', 'do_maximum']:
                    handler = getattr(self, step)
                    resp = self.do(handler=handler, lst_data=lst_data, alter_key=alter_key)
                    if resp:
                        logger.info(f'{resp}')

        except Exception as e:
            logger.exception(e)


logging.basicConfig(level=logging.DEBUG)
wb = WriteBackMixin()
# wb.load_alters_data(alter_source='x')
wb.run(alter_source='x')
# print(wb.alters_map)
