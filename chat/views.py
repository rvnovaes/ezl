from datetime import datetime
from django.views.generic import ListView
from chat.models import Chat, UnreadMessage, Message
from core.views import CustomLoginRequiredView
from django.http import JsonResponse
from django.views.generic import View
from django.db.models import Count, Q
from django.core import serializers
import json
from core.models import Person
from core.models import Office
from core.utils import get_office_session
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import  get_groups_with_perms
from django.shortcuts import render
from task.models import Task
from django.forms.models import model_to_dict

def chat_teste(request):
    return render(request, 'chat/chat_test.html', {'teste': {'teste': 'tetando'}})

class ChatListView(ListView):
    model = Chat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ChatCountMessages(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        has_groups = request.GET.get('has_groups', 'false') == 'true'
        data = {
            'all_messages': UnreadMessage.objects.filter(
                user_by_message__user_by_chat=self.request.user).count(),
        }
        if has_groups:
            data['grouped_messages'] = list(UnreadMessage.objects.filter(
                user_by_message__user_by_chat=self.request.user
                ).values('message__chat__pk').annotate(quantity=Count('id')).order_by())

        return JsonResponse(data)


class ChatReadMessages(CustomLoginRequiredView, View):
    def post(self, request, *args, **kwargs):
        chat_id = json.loads(request.body).get('chat_id')
        chat = Chat.objects.filter(pk=int(chat_id)).first()
        if chat:
            UnreadMessage.objects.filter(user_by_message__user_by_chat=self.request.user,
                                         message__chat=chat).delete()
        return JsonResponse({'status': 'ok'})


class ChatGetMessages(CustomLoginRequiredView, View):
    def post(self, request, *args, **kwargs):
        chat_id = request.POST.get('chat_id')
        qry_message = Message.objects.filter(
            chat_id=chat_id
        )
        qry_chat = Chat.objects.get(
            id=chat_id
        )
        messages = map(
            lambda x: {
                'text': x.message,
                'message_create_date': x.create_date.strftime("%d/%m/%Y às %H:%M:%S"),
                'user': x.create_user.username
                },
            qry_message
        )
        data = {
            'messages': list(messages),
            'chat': {
                'pk': qry_chat.pk,
                'description': qry_chat.description,
                'back_url': qry_chat.back_url,
                'title': qry_chat.title
            }
        }
        return JsonResponse(data)

class ChatOfficeContactView(CustomLoginRequiredView, View):
    @staticmethod
    def add_count_unread_message(user, contact_offices):
        for office in contact_offices:
            unread_message_quanty = UnreadMessage.objects.filter(
                user_by_message__user_by_chat=user,
                message__chat__offices__id=office.get('pk')).count()
            office['unread_message_quanty'] = unread_message_quanty
        return contact_offices

    def get(self, request, *args, **kwargs):
        current_office = get_office_session(request)
        chats = Chat.objects.filter(users__user_by_chat=self.request.user, users__is_active=True).order_by(
            'pk').distinct('pk')
        data = list(Office.objects.filter(chats__in=chats,).values('pk', 'legal_name').distinct('pk'))
        data = self.add_count_unread_message(request.user, data)
        return JsonResponse(data, safe=False)


class ChatsByOfficeView(CustomLoginRequiredView, View):
    @staticmethod
    def add_count_unread_message(user, chats):
        # Pegamos todos os chats do usuário que possuem mensagens não lidas
        unread_chats = UnreadMessage.objects.filter(
            user_by_message__user_by_chat=user,
        ).values('message__chat').annotate(count=Count('id'))
        items = []
        unread_chats_dict = dict({(item['message__chat'], item['count']) for item in unread_chats})
        for chat in chats:
            last_message = chat.messages.last()
            item = {
                "id": chat.id,
                "unread_message_quanty": unread_chats_dict[chat.id] if chat.id in unread_chats_dict else 0,
                "title": chat.title,
                "alter_date": chat.alter_date if not last_message else last_message.create_date,
                "label": chat.label,
                "has_messages": chat.messages.exists()
            }
            items.append(item)
        return list(reversed(sorted(items, key=lambda x: x['alter_date'])))

    def get(self, request, *args, **kwargs):
        filters = {
            "users__user_by_chat": self.request.user,
            "users__is_active": True,
        }
        office_id = int(request.GET.get('office'))
        since = request.GET.get('since')
        exclude_empty = request.GET.get('exclude_empty', False) == 'true'

        if exclude_empty:
            filters["messages__isnull"] = False

        if since:
            since = datetime.strptime(since.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            filters["alter_date__gt"] = since
            filters["messages__create_date__gt"] = since

        office = Office.objects.get(pk=office_id)
        chats = office.chats.filter(**filters)\
                    .distinct('id')\
                    .prefetch_related('messages')\
                    .order_by('id')
        #            .order_by('-messages__create_date', 'id')
        data = self.add_count_unread_message(request.user, chats)
        return JsonResponse(data, safe=False)

class ChatMenssage(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):        
        chat = Chat.objects.get(pk=int(request.GET.get('chat')))
        messages = list(chat.messages.all().values('message', 'create_user__username', 'create_user_id', 'create_date'))
        office = get_office_session(request)        
        task = chat.task_set.filter(pk=chat.label.split('-')[1]).first()                
        if task.parent and task.parent.office == office:
            task_id = task.parent.pk
        elif task.get_child and task.get_child.office == office:
            task_id = task.get_child.pk
        else:
            task_id = task.pk
        data = {
            "messages": messages,
            "request_user_id": request.user.id,
            "chat": model_to_dict(chat, fields=([field.name for field in chat._meta.fields])),
            "task": task_id
        }
        return  JsonResponse(data, safe=False)

class InternalChatOffices(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        task = Task.objects.get(pk=int(request.GET.get('task')))
        data = []
        if task.parent:
            data.append({
                'chat': task.chat.pk, # "Deve ser o pk da propria task"
                'office_pk': task.parent.office.pk, #"Deve ser o pk do office do parent"
                'office_legal_name': task.parent.office.legal_name
            })
        for task_child in task.child.all():
            data.append({
                'chat': task_child.chat.pk, # "Deve ser o pk do chat da task filha"
                'office_pk': task_child.office.pk,
                'office_legal_name': task_child.office.legal_name
            })
        if not all([task.parent, task.child.exists()]):
            data.append({
                'chat': task.chat.pk, # "Deve ser o pk do chat da task filha"
                'office_pk': task.office.pk,
                'office_legal_name': task.office.legal_name
            })
        return JsonResponse(data, safe=False)


class UnreadMessageView(CustomLoginRequiredView, View):
    def post(self, request, *args, **kwargs):        
        chat_id = json.loads(request.body).get('chat')
        chat = Chat.objects.get(pk=chat_id)
        if (chat.messages.exists()):
            user_by_chat = chat.users.filter(user_by_chat=request.user).first()            
            UnreadMessage.objects.create(
                create_user=request.user, message=chat.messages.latest('pk'), user_by_message=user_by_chat)
        return JsonResponse({'status': 'ok'})
