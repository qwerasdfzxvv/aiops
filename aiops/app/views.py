from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WeChatGroup, WeChatMessage, ApplicationSystem
from .serializers import WeChatGroupSerializer, WeChatMessageSerializer, ApplicationSystemSerializer, \
    CommonGroupChatSerializer
import requests
from faker import Faker
import logging
fake = Faker(locale='zh_CN')

logger=logging.getLogger(__name__)
class WeChatGroupViewSet(viewsets.ModelViewSet):
    queryset = WeChatGroup.objects.all()
    serializer_class = WeChatGroupSerializer

    def serialize_and_request(self, data, method, url):
        serializer=CommonGroupChatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        req_data = serializer.validated_data['reqData']
        return self.do_http_request(method, url, json=req_data)
    def do_http_request(self, method, url, params=None, data=None, json=None, headers=None, timeout=None):
        data = {"errcode": 0, "errmsg": "ok"}
        if 'create' in url:
            data['chatid'] = fake.uuid4()
            data['name'] = fake.uuid4()
            data['chatid'] = fake.uuid4()
            return data
        if 'get' in url:
            data['chat_info'] = {
                "chatid": fake.uuid4(),
                "name": fake.name(),
                "owner": fake.uuid4(),
                "userlist": [fake.uuid4() for i in range(1, 5)]
            }
            return data
        if 'userlist' in url:
            data['userlist'] = [fake.uuid4() for i in range(1, 5)]
            return data
        return data

        # try:
        #     response = requests.request(method, url, params=params, data=data, json=json, headers=headers,
        #                                 timeout=timeout)
        #     response.raise_for_status()
        #     return response.json()
        # except requests.exceptions.RequestException as e:
        #     raise RuntimeError(f"HTTP请求失败: {e}")
    @action(detail=False, methods=['POST'], url_path='run')
    def run(self, request, *args, **kwargs):
        data = request.data.copy()
        if not isinstance(data, dict):
            return JsonResponse({"error": "无效的数据格式"}, status=400)
        chatid = data.get('chatid')
        logger.info('chatid=%s', chatid)
        if not chatid:
            data['chatid'] = self.create_group_chat(data)
        if chatid and data.get('user_list'):
            user_add_list = self.set_user_add_list(data)
            chat_info = self.get_group_chat(data)
            data['user_add_list'] = user_add_list
            data['user_del_list'] = list(set(chat_info['userlist']) - set(data['user_add_list']))
        self.update_group_chat(data)
        return JsonResponse(data)

    def set_user_add_list(self, data):
        resp = self.do_http_request('POST', 'https://qyapi.weixin.qq.com/cgi-bin/appchat/userlist',json=data)
        return resp['userlist']

    def create_group_chat(self, data):
        data['reqType'] = 'create'
        resp = self.serialize_and_request(data, 'POST', 'https://qyapi.weixin.qq.com/cgi-bin/appchat/create')
        # # 保存群聊信息到数据库
        # WeChatGroup.objects.create(
        #     name=data.get('name'),
        #     chat_id=resp['chatid'],
        #     owner=data.get('owner')
        # )
        return resp['chatid']

    def get_group_chat(self, data):
        data['reqType'] = 'get'
        resp = self.serialize_and_request(data, 'GET', 'https://qyapi.weixin.qq.com/cgi-bin/appchat/get')
        return resp['chat_info']

    def update_group_chat(self, data):
        data['reqType'] = 'update'
        self.serialize_and_request(data, 'POST', 'https://qyapi.weixin.qq.com/cgi-bin/appchat/update')


    def send_group_chat(self, data):
        data['reqType'] = 'send'
        self.serialize_and_request(data, 'POST', 'https://qyapi.weixin.qq.com/cgi-bin/appchat/send')
    #
# class WeChatMessageViewSet(viewsets.ModelViewSet):
#     queryset = WeChatMessage.objects.all()
#     serializer_class = WeChatMessageSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 调用企业微信API发送消息
#         response = requests.post(
#             "https://qyapi.weixin.qq.com/cgi-bin/appchat/send",
#             params={"access_token": "YOUR_ACCESS_TOKEN"},
#             json={
#                 "chatid": serializer.validated_data['group'].chat_id,
#                 "msgtype": serializer.validated_data['content_type'],
#                 serializer.validated_data['content_type']: {
#                     "content" if serializer.validated_data['content_type'] == 'text' else "media_id":
#                         serializer.validated_data['content']
#                 }
#             }
#         )
#         response.raise_for_status()
#
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ApplicationSystemViewSet(viewsets.ModelViewSet):
    queryset = ApplicationSystem.objects.all()
    serializer_class = ApplicationSystemSerializer
