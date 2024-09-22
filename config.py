from .base import CheckBase
from faker import Faker

fake = Faker()


class Config(CheckBase):
    name = 'Config'
    description = '配置中心'
    version = '1.0'

    check_methods = [
        {'method': 'check_status', 'label': fake.name(), },
        {'method': 'check_merge', 'label': fake.name()},
    ]

    def __init__(self):
        # super().__init__()
        self.queues = []
        for _ in range(10):
            self.queues.append({
                'id': fake.uuid4(),
                'label': fake.name(),
                'deploy_status': fake.random_int(min=0, max=9),
            })

    def create_nodes(self, queues):
        queues = [self.get_title_queue()] + queues
        return super().create_nodes(queues)

    def check_merge(self):
        status = {
            'open': '未合并',
            'closed': '已合并'
        }
        for queue in self.queues:
            if queue['deploy_status']==0:
                continue
            merge_state = fake.random_element(['open', 'closed'])
            result = {
                'check_type': 'check_merge',
                'status': merge_state == 'closed',
                'remark': status[merge_state],
                'merge_state': merge_state
            }
            self.result[queue['id']].append(result)

