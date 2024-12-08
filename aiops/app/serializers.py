from rest_framework import serializers
from .models import WeChatGroup, WeChatMessage, ApplicationSystem

import logging

logger = logging.getLogger(__name__)


class WeChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChatGroup
        fields = ['id', 'name', 'chat_id', 'owner']


class WeChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChatMessage
        fields = ['id', 'chat_id', 'content_type', 'content', 'timestamp']


class ApplicationSystemSerializer(serializers.ModelSerializer):
    users = serializers.ListField()

    class Meta:
        model = ApplicationSystem
        read_only_fields = ('users',)
        fields = read_only_fields


class CreateGroupChatSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    user_list = serializers.ListField(child=serializers.CharField(max_length=255), min_length=2, allow_empty=False)
    owner = serializers.CharField(max_length=255, required=False, allow_blank=True)
    chatid = serializers.CharField(max_length=255, required=False, allow_blank=True)


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=255)
    chatid = serializers.CharField(max_length=255)
    content_type = serializers.ChoiceField(choices=['text', 'image'])


class UpdateGroupChatSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    chatid = serializers.CharField(max_length=255)
    owner = serializers.CharField(max_length=255, required=False, allow_blank=True)
    user_add_list = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
    user_del_list = serializers.ListField(child=serializers.CharField(max_length=255), required=False)


class GetGroupChatSerializer(serializers.Serializer):
    chatid = serializers.CharField(max_length=255)


class CommonGroupChatSerializer(serializers.Serializer):
    reqType = serializers.ChoiceField(choices=['create', 'send', 'update', 'get'])
    apiName = serializers.CharField(max_length=255, allow_blank=False, required=True)
    apiMethod = serializers.CharField(max_length=255, allow_blank=False, required=True)
    apiUrl = serializers.CharField(max_length=255, allow_blank=False, required=True)
    reqData = serializers.DictField(allow_empty=False)

    apis = {
        'create': {
            'apiName': '创建群聊',
            'apiMethod': 'POST',
            'apiUrl': '/appchat/create',
        },
        'send': {
            'apiName': '发送消息',
            'apiMethod': 'POST',
            'apiUrl': '/message/send',
        },
        'update': {
            'apiName': '更新群聊',
            'apiMethod': 'POST',
            'apiUrl': '/appchat/update',
        },
        'get': {
            'apiName': '获取群聊',
            'apiMethod': 'GET',
            'apiUrl': '/appchat/get',
        }
    }

    class Meta:
        fields = ['apiName', 'apiMethod', 'apiUrl', 'reqType', 'reqData']

    def to_internal_value(self, data):
        logger.debug("Received data: %s", data)
        req_type = data.get('reqType')
        if req_type not in self.apis:
            raise serializers.ValidationError("Invalid request type")

        serializer = {
            'create': CreateGroupChatSerializer,
            'send': SendMessageSerializer,
            'update': UpdateGroupChatSerializer,
            'get': GetGroupChatSerializer
        }[req_type](data=data)

        logger.debug("Using serializer: %s", serializer.__class__.__name__)
        serializer.is_valid(raise_exception=True)
        logger.debug("Validated data: %s", serializer.validated_data)
        data['reqData'] = serializer.validated_data
        data['apiMethod'] = self.apis[req_type]['apiMethod']
        data['apiName'] = self.apis[req_type]['apiName']
        data['apiUrl'] = self.apis[req_type]['apiUrl']
        return super().to_internal_value(data)
