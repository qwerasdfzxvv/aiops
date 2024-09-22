from .base import CheckBase
from faker import Faker

fake = Faker()


class Vm(CheckBase):
    name = 'Vm'
    description = '虚拟机'
    version = '1.0'
    check_methods = [
        {'method': 'check_status', 'label': fake.name(), },
        # {'method': 'check_merge', 'label': fake.name()},
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
