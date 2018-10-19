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
    task_number = serializers.SerializerMethodField()
    opposing_party = serializers.SerializerMethodField()
    final_deadline_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ('id', 'create_date', 'title', 'label', 'messages', 'opposing_party', 
            'task_number', 'final_deadline_date')

    def get_task_number(self, obj):
        return obj.tasks_company_chat.latest('pk').task_number                

    def get_opposing_party(self, obj):
        return obj.tasks_company_chat.latest('pk').opposing_party         

    def get_final_deadline_date(self, obj): 
        final_deadline_date = obj.tasks_company_chat.latest('pk').final_deadline_date
        return final_deadline_date.strftime('%d/%m/%Y %H:%M')        


class UnreadMessageSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()
    chat = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    task_number = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    opposing_party = serializers.SerializerMethodField()
    final_deadline_date = serializers.SerializerMethodField()

    class Meta:
        model = UnreadMessage
        fields = ('id', 'create_date', 'create_user', 'message', 'office',
                  'chat', 'task', 'task_status', 'opposing_party', 'task_number', 
                  'final_deadline_date')

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

    def get_task_number(self, obj):
        return obj.message.chat.tasks_company_chat.latest('pk').task_number                

    def get_opposing_party(self, obj):
        return obj.message.chat.tasks_company_chat.latest('pk').opposing_party        

    def get_final_deadline_date(self, obj): 
        final_deadline_date = obj.message.chat.tasks_company_chat.latest('pk').final_deadline_date
        return final_deadline_date.strftime('%d/%m/%Y %H:%M')                