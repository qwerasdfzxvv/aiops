from abc import ABC, abstractmethod
from faker import Faker
from collections import defaultdict
from itertools import groupby
fake = Faker()


class GraphBuilder(ABC):
    check_methods = []

    @abstractmethod
    def build_nodes(self):
        pass

    @abstractmethod
    def build_edges(self):
        pass


class ConfigGraphBuilder(GraphBuilder):
    check_methods = [
        {'method': 'check_status', 'label': fake.name(), 'queueId': fake.uuid4()},
        {'method': 'check_merge', 'label': fake.name(), 'queueId': fake.uuid4()},
    ]
    description = '配置中心'

    name = 'Config'

    def __init__(self, orders):
        self.nodes = []
        self.edges = []
        self._queues = orders[self.name] or []
        self.queues = []
        self.result = defaultdict(list)
        self.init_data()

    def init_data(self):
        print('init data')
        if not self._queues:
            return None
        for method in self.check_methods:
            getattr(self, method['method'])()

    def check_status(self):
        print('check status')
        for queue in self._queues:
            self.result[queue['id']].append(
                {**queue, **{'color': fake.color(), 'status': fake.pyint(min_value=0, max_value=2)}})

    def check_merge(self):
        print('check merge')
        for queue in self._queues:
            self.result[queue['id']].append(
                {**queue, **{'color': fake.color(), 'status': fake.pyint(min_value=0, max_value=2)}})

    def build_nodes(self):
        title_node = {'id': 'title', 'label': self.description}
        self.nodes.append(title_node)
        for queue in self._queues:
            state = all([i['status'] == 1 for i in self.result[queue['id']]])
            self.nodes.append({**queue, **{'color': fake.color(), 'status': state}})

    def build_edges(self):
        for queue in self._queues:
            self.edges.append(queue)


class ContainerGraphBuilder(GraphBuilder):
    check_methods = [
        {'method': 'check_status', 'label': fake.name(), 'queueId': fake.uuid4()},
        {'method': 'check_merge', 'label': fake.name(), 'queueId': fake.uuid4()},
    ]
    description = '容器中心'

    name = 'Container'

    def __init__(self, orders):
        self.nodes = []
        self.edges = []
        self._queues = orders[self.name] or []
        self.queues = []
        self.result = defaultdict(list)
        self.init_data()

    def init_data(self):
        print('init data')
        if not self._queues:
            return None
        for method in self.check_methods:
            getattr(self, method['method'])()

    def check_status(self):
        print('check status')
        for queue in self._queues:
            self.result[queue['id']].append(
                {**queue, **{'color': fake.color(), 'status': fake.pyint(min_value=0, max_value=2)}})

    def check_merge(self):
        print('check merge')
        for queue in self._queues:
            self.result[queue['id']].append(
                {**queue, **{'color': fake.color(), 'status': fake.pyint(min_value=0, max_value=2)}})

    def build_nodes(self):
        data=sorted(self._queues, key=lambda x: x['region'])
        for k,g in groupby(data, key=lambda x: x['region']):
            child_nodes=[]
            title_node = {'id': k, 'label': k}
            child_nodes.append(title_node)
            for queue in g:
                state = all([i['status'] == 1 for i in self.result[queue['id']]])
                child_nodes.append({**queue, **{'color': fake.color(), 'status': state}})
            self.nodes.append(child_nodes)

    def build_edges(self):
        data = sorted(self._queues, key=lambda x: x['region'])
        for k, g in groupby(data, key=lambda x: x['region']):
            child_edges = []
            for queue in g:
                child_edges.append(queue)
            self.edges.append(child_edges)


class VmGraphBuilder(GraphBuilder):
    check_methods = [
        {'method': 'check_status', 'label': fake.name(), },
        {'method': 'check_merge', 'label': fake.name()},
    ]
    description = '虚拟机中心'

    def __init__(self):
        self.nodes = []
        self.edges = []

    def build_nodes(self):
        pass

    def build_edges(self):
        pass


class Director:
    def __init__(self, builder):
        self.builder = builder

    def construct_graph(self, ):
        self.builder.build_nodes()
        self.builder.build_edges()
        return {
            "nodes": [node for node in self.builder.nodes],
            "edges": [edge for edge in self.builder.edges]
        }


Config = [{'id': fake.uuid4(), 'label': fake.name()} for i in range(10)]
Container = [{'id': fake.uuid4(), 'label': fake.name(),'region': fake.random_element(elements=['beijing','shanghai','guangzhou'])} for i in range(20)]

orders = {
    'Config': Config,
    'Container': Container
}

configbuilder = ConfigGraphBuilder(orders=orders)
director = Director(configbuilder)
graph_data = director.construct_graph()
print(graph_data)
print(len(graph_data['nodes']))
print(len(graph_data['edges']))
container_builder = ContainerGraphBuilder(orders=orders)
director = Director(container_builder)
graph_data01 = director.construct_graph()

print(graph_data01)
print(len(graph_data01['nodes']))
print(len(graph_data01['edges']))
# 定义边的类型
EDGE_TYPES = ['left', 'right']
node_columns=[graph_data['nodes'],*graph_data01['nodes']]
num_columns=len(node_columns)
print(num_columns)
x_offset = 100  # 每列的起始 x 坐标
y_offset = 200  # 每个节点的起始 y 坐标
spacing_x = 200  # 列间距
spacing_y = 100  # 行间距

nodes = []
for col in range(num_columns):
    for row in range(len(node_columns[col])):
        x = x_offset + col * spacing_x
        y = y_offset + row * spacing_y
        node = {
            "id": node_columns[col][row]['id'],
            "x": x,
            "y": y,
            "width": 100,
            "height": 40,
            "shape": "rect",
            "label": node_columns[col][row]['label'],
        }
        nodes.append(node)

edges_columns=[graph_data['edges'],*graph_data01['edges']]
edges_num_columns=len(edges_columns)

# 生成同一列内的边
edges = []
for col in edges_columns:
    for source, target in zip(col[:-1], col[1:]):
        for side in ['left', 'right']:
            edge = {
                "source": {"cell": source['id']},
                "target": {"cell": target['id']},
                "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
                "router": {"name": "oneSide", "args": {"padding": 10, "side": side}}
            }
            edges.append(edge)
for col_index in range(len(edges_columns) - 1):
    col_x = (col_index + 1) * 150
    edge_id = f"{ edges_columns[col_index][0]['id']}-{ edges_columns[col_index + 1][0]['id']}"
    edge = {
        "id": edge_id,
        "source": {"cell": edges_columns[col_index][0]['id']},
        "target": {"cell": edges_columns[col_index+1][0]['id']},
        "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
    }
    edges.append(edge)
nodw_max=max([ len(i) for i in node_columns ])
print(nodw_max)
for col_index in range(num_columns+1):
    col_x = x_offset + col_index * spacing_x-50
    edge = {
        "source": {'x':col_x,'y': spacing_y},
        "target": {'x':col_x,'y': nodw_max*(spacing_y+40)},
        "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
    }
    edges.append(edge)


print(nodes)
print(edges)
import json
print('export const data=',json.dumps({
    'nodes':nodes,
    'edges':edges
}))

edge = {
        "source": {'x':x_offset-50,'y': y_offset + 1 * spacing_y+20},
        "target": {'x':3000,'y': y_offset + 1 * spacing_y+20},
        "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
    }
edges.append(edge)

with open('D:\\program\\django-vue-admin-main\\web\\src\\views\\flow\\data.js','w') as f:
    f.write('export const data='+json.dumps({'nodes':nodes,'edges':edges}))
