from rest_framework import serializers
from .models import Chat, UnreadMessage, Message
import json


class ChatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Chat
		fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = ('message', )


class UnreadMessageSerializer(serializers.ModelSerializer):	
	message = serializers.SerializerMethodField()
	office = serializers.SerializerMethodField()
	chat = serializers.SerializerMethodField()
	task = serializers.SerializerMethodField()

	class Meta:
		model = UnreadMessage
		fields = ('id', 'create_date', 'create_user', 'message', 'office', 'chat', 'task')

	def get_message(self, obj):
		return obj.message.message

	def get_office(self, obj):
		if obj.message.chat.offices.exists():
			office = obj.message.chat.offices.first()
			return {'name': office.legal_name, 'logo': office.logo.url}
		return {}

	def get_chat(self, obj):
		return {'title': obj.message.chat.title}

	def get_task(self, obj):
		return obj.message.chat.tasks_company_chat.latest('pk').pk