from faker import Faker

fake = Faker()
from collections import defaultdict


class CheckBase:
    name = 'base'
    description = 'base'

    stop_check = False

    check_methods = []

    result = defaultdict(list)

    queues=[]


    def get_title_queue(self, id=None, label=None):
        id = id or self.name
        label = label or self.description
        title_queue = {
            'id': id,
            'color': fake.color(),
            'label': label,
            'status': 'ok',
        }
        return title_queue

    def create_nodes(self, queues):
        nodes = []
        width = 200
        height = 50
        for queue in queues:
            print(queue)
            node = {
                "id": queue['id'],
                "shape": "rect",
                "width": width,
                "height": height,
                "label": queue['label'],
                "data": {'queue': queue, 'result': self.result[queue['id']]},
                "attrs": {"body": {"stroke": "#8f8f8f", "strokeWidth": 1, "fill": queue['color']}}
            }
            nodes.append(node)
        return nodes

    def create_edges(self, queues):
        edges = []
        for source, target in zip(queues[:-1], queues[1:]):
            for side in ['left', 'right']:
                edge = {
                    "source": {"cell": source['id']},
                    "target": {"cell": target['id']},
                    "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
                    "router": {"name": "oneSide", "args": {"padding": 10, "side": side}}
                }
                edges.append(edge)
        return edges

    def create_graph(self, queues):
        if not queues:
            return {}
        return {
            'nodes': self.create_nodes(queues),
            'edges': self.create_edges(queues),
        }

    def check_status(self):
        status = {
            0: '未布署',
            1: '备份成功',
            2: '备份失败',
            3: '发布成功',
            4: '发布失败',
            5: '回滚成功',
            6: '回滚失败',
            7: '回滚中',
            8: '发布中',
            9: '备份中',
        }
        for queue in self.queues:
            result = {
                'check_type': 'check_status',
                'status': queue['deploy_status'] == 3,
                'remark': status[queue['deploy_status']],
                'deploy_status': queue['deploy_status']
            }
            self.result[queue['id']].append(result)


    def update_queue_result(self):
        """
        1. 未发布  #dddddd
        2. 发布成功 green
        3. 发布失败 red
        4. 发布中 blue
        """
        for queue in self.queues:
            if queue['deploy_status']  in [0]:
                queue.update({'color': '#dddddd'})
            if queue['deploy_status'] in [2, 4,5, 6]:
                queue.update({'color': 'red'})
            if queue['deploy_status'] in [1, 7, 8, 9]:
                queue.update({'color': 'blue'})
                continue
            # 成功并且验证通过
            if queue['deploy_status'] in [3]:
                if all([x['status'] for x in self.result[queue['id']]]):
                    queue.update({'color': 'green'})
                else:
                    queue.update({'color': 'red'})

    def run(self):

        for cm in self.check_methods:
            print(self.__class__.__name__,cm)
            method = getattr(self, cm['method'])
            method()

        self.update_queue_result()
        return self.create_graph(self.queues)
