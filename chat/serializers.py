from rest_framework import serializers
from .models import Chat, UnreadMessage, Message
import json


class MessageSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'create_user', 'create_date', 'message', 'username')

    def get_username(self, obj):
        return obj.create_user.username


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'create_date', 'title', 'label', 'messages')


class UnreadMessageSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()
    chat = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()

    class Meta:
        model = UnreadMessage
        fields = ('id', 'create_date', 'create_user', 'message', 'office',
                  'chat', 'task', 'task_status')

    def get_message(self, obj):
        return obj.message.message

    def get_office(self, obj):
        if obj.message.chat.offices.exists():
            office = obj.message.chat.offices.first()
            return {
                'name': office.legal_name,
                'logo': office.logo.url if office.logo else ''
            }
        return {}

    def get_chat(self, obj):
        return {'title': obj.message.chat.title, 'id': obj.message.chat.pk}

    def get_task(self, obj):
        return obj.message.chat.tasks_company_chat.latest('pk').pk

    def get_task_status(self, obj):
        return obj.message.chat.tasks_company_chat.latest('pk').status.name