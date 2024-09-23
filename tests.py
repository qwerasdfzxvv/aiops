# from unittest import TestCase

from django.db import connection

from .views import PolarisModelViewSet

from itertools import count
from django.test import TestCase,TransactionTestCase
import json


class PolarisTestCase(TransactionTestCase):

    def test_config(self):
        from .chker.config import Config
        from .chker.container import Container
        from .chker.vm import Vm
        vm = Vm().run()
        container=Container().run()
        config = Config().run()
        data={}
        data['edges']=vm['edges']+container['edges']+config['edges']
        nodes=[]
        width = 200
        height = 50
        margin=30
        all_nodes=[[],vm['nodes'],*container['nodes'],config['nodes']]
        width_iter = count(margin, width+margin*2)
        for d in all_nodes:
            x=next(width_iter)
            edge = {
                "source": {'x':x+width+margin,'y':0},
                "target": {'x':x+width+margin,'y':6000},
                "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
            }
            data['edges'].append(edge)
            y=count(margin, 100)
            for i in d:
                i['x']=x
                i['y']=next(y)
                nodes.append(i)
        data['edges'].append({
                "source": {'x':margin+width,'y':margin+height+margin+height},
                "target": {'x':next(width_iter),'y':margin+height+margin+height},
                "zIndex": -1,
                "attrs": {"line": {"stroke": "#8f8f8f", "strokeWidth": 1, "targetMarker": ""}},
            })
        data['nodes']=nodes
        max_height=max([ len(i) for i in all_nodes])*(height+margin)
        max_width =len(all_nodes)*(width+margin)
        print(max_height,max_width)

        with open('D:\\program\\django-vue-admin-main\\web\\src\\views\\flow\\data.js','w') as f:
            f.write('export const data='+json.dumps({'nodes':data['nodes'],'edges':data['edges']}))
        print('export const data=',json.dumps(data))





