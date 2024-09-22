from .base import CheckBase
from faker import Faker
fake = Faker('zh_CN')

from collections import defaultdict



class Container(CheckBase):
    name = 'Container'
    description = '容器'
    version = '1.0'

    check_methods = [
        {'method': 'check_status', 'label': fake.name(), },
        {'method': 'check_pod', 'label': fake.name()},
        {'method': 'check_image', 'label': fake.name()},
    ]

    def __init__(self):
        # super().__init__()
        self.queues = []
        for _ in range(30):
            self.queues.append({
                'id': fake.uuid4(),
                'label': fake.name(),
                'region': fake.random_element(['ap-shanghai', 'ap-beijing', 'ap-chengdu']),
                'deploy_status': fake.random_int(min=0, max=9),
            })

    def check_pod(self):

        status = {
            'runing': '运行中',
            'failed': '启动失败'
        }
        for queue in self.queues:
            if queue['deploy_status']==0:
                continue
            pod_state = fake.random_element(['runing', 'failed'])
            result = {
                'check_type': 'check_pod',
                'status': pod_state == 'runing',
                'remark': status[pod_state],
                'pod_state': pod_state
            }
            self.result[queue['id']].append(result)


    def check_image(self):
        status = {
            'ok': '境像一致',
            'no': '境像不一致'
        }
        for queue in self.queues:
            if queue['deploy_status']==0:
                continue
            image_state = fake.random_element(['ok', 'no'])
            result = {
                'check_type': 'check_image',
                'status': image_state == 'ok',
                'remark': status[image_state],
                'image_state': image_state
            }
            self.result[queue['id']].append(result)



    def create_nodes(self, queues):
        nodes=[]
        regions = defaultdict(list)
        for queue in queues:
            regions[queue['region']].append(queue)
        for k,v in regions.items():
            v.insert(0, self.get_title_queue(id=k, label=k))
            node=super().create_nodes(queues=v)
            nodes.append(node)
        return nodes

    def create_edges(self, queues):
        edges = []
        regions = defaultdict(list)
        for queue in queues:
            regions[queue['region']].append(queue)
        for k,v in regions.items():
            edge=super().create_edges(queues=v)
            edges+=edge
        return edges

