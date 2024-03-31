import concurrent
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
from retrying import retry  # 需要先通过 `pip install retrying` 安装retrying库
import time
from random import random, randint

logger = logging.getLogger(__name__)


class MonitorData:
    def __init__(self, url):
        self.url = url
        self.url_map = {}

    # 使用retrying库装饰器实现重试机制
    @retry(stop_max_attempt_number=3, wait_fixed=2000)  # 最多重试3次，每次间隔2秒
    def fetch_data(self, url):
        response = requests.get(url)
        response.raise_for_status()  # 如果非200状态码，则抛出异常
        return response.json()

    # 假设有一个检查数据是否异常的函数
    def is_data_abnormal(self, data, url):
        logger.info(data)
        id='EVENT_{}'.format(url.split('?')[1])
        print(self.url_map.get(id))
        # 这里根据实际情况编写逻辑判断数据是否异常
        # 示例：如果数据大于某个阈值则认为是异常
        threshold = 10
        return data > threshold

    # 假设有一个推送通知的方法
    def send_notification(self, data):
        logger.info(data)
        print(self.url_map)
        time.sleep(randint(5, 10))
        # 这里根据实际情况调用通知服务接口，如邮件、短信、钉钉机器人等
        print(f"发送异常数据通知：{data}")

    def run(self):
        # 监控数据API地址
        thread_list = []
        api_url = "https://mock.presstime.cn/mock/6607f5193d7acdc52db6fe3f/example/mock"

        # 需要获取监控数据的列表
        urls = []
        for i in range(20):
            tt=randint(1, 1000)
            url=api_url + "?{0}".format(tt)
            urls.append(url)
        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.fetch_data, url): (index, url) for index, url in enumerate(urls)}
            for future in concurrent.futures.as_completed(future_to_url):
                index, url = future_to_url[future]
                try:
                    data = future.result()
                    logger.info(data)
                    if self.is_data_abnormal(data['data']['value'], url):  # 根据实际数据结构调整
                        # 异步发送通知
                        t = threading.Thread(
                            target=self.send_notification,
                            name='thread_{0}'.format(index),
                            args=(data,),
                            daemon=True
                        )
                        t.start()
                        thread_list.append(t)
                except Exception as exc:
                    print(f"获取{url}数据并处理时发生错误: {exc}")

        for i in thread_list:
            i.join(timeout=10)
        print("++++++++++++++++++++++++++++++++++")


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(funcName)s - %(thread)d - %(process)d - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
MonitorData(url='').run()
