from datetime import datetime
import time
from django.views.generic import ListView
from chat.models import Chat, UnreadMessage, Message
from core.views import CustomLoginRequiredView
from django.http import JsonResponse
from django.views.generic import View
from django.db.models import Count, Q
import json
from core.models import Office, Team
from core.utils import get_office_session
from django.shortcuts import render
from task.models import Task, TaskStatus
from django.forms.models import model_to_dict


class ChatListView(ListView):
    model = Chat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ChatCountMessages(View):
    def get(self, request, *args, **kwargs):
        has_groups = request.GET.get('has_groups', 'false') == 'true'
        users = [request.user.pk]
        users.extend(Team.get_members(request.user))
        data = {
            'all_messages':
            UnreadMessage.objects.filter(
                user_by_message__user_by_chat__in=users).count(),
        }
        if has_groups:
            data['grouped_messages'] = list(
                UnreadMessage.objects.filter(
                    user_by_message__user_by_chat__in=users).values('message__chat__pk').annotate(
                        quantity=Count('id')).order_by())

        return JsonResponse(data)


class ChatReadMessages(View):
    def post(self, request, *args, **kwargs):
        chat_id = json.loads(request.body).get('chat_id')
        chat = Chat.objects.filter(pk=int(chat_id)).first()
        if chat:
            UnreadMessage.objects.filter(
                user_by_message__user_by_chat=self.request.user,
                message__chat=chat).delete()
        return JsonResponse({'status': 'ok'})


class ChatGetMessages(View):
    def post(self, request, *args, **kwargs):
        chat_id = request.POST.get('chat_id')
        qry_message = Message.objects.filter(chat_id=chat_id)
        qry_chat = Chat.objects.get(id=chat_id)
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


class ChatOfficeContactView(View):
    @staticmethod
    def add_count_unread_message(users, contact_offices):
        min_date = datetime.strptime('1970-01-01', '%Y-%m-%d')
        for office in contact_offices:
            unread_messages = UnreadMessage.objects.filter(
                user_by_message__user_by_chat__in=users,
                message__chat__offices__id=office.get('pk'))
            unread_message_quanty = unread_messages.count()
            latest_unread_message = min_date
            if unread_messages:
                latest_unread_message = unread_messages.latest(
                    'create_date').create_date
            office['unread_message_quanty'] = unread_message_quanty
            office['latest_unread_message'] = int(
                time.mktime(latest_unread_message.timetuple()))
        return sorted(
            contact_offices,
            key=lambda i: i.get('latest_unread_message'),
            reverse=True)

    def get(self, request, *args, **kwargs):
        users = [request.user.pk]
        users.extend(Team.get_members(request.user))
        current_office = get_office_session(request)
        chats = Chat.objects.filter(
            users__user_by_chat__in=users,
            users__is_active=True).order_by('pk').distinct('pk')
        data = list(
            Office.objects.filter(chats__in=chats, ).values(
                'pk', 'legal_name').distinct('pk'))
        data = self.add_count_unread_message(users, data)
        return JsonResponse(data, safe=False)


class ChatsByOfficeView(View):
    @staticmethod
    def add_count_unread_message(users, chats):
        # Pegamos todos os chats do usuário que possuem mensagens não lidas
        unread_chats = UnreadMessage.objects.filter(
            user_by_message__user_by_chat__in=users, ).values(
                'message__chat').annotate(count=Count('id'))
        items = []
        unread_chats_dict = dict({(item['message__chat'], item['count'])
                                  for item in unread_chats})
        for chat in chats:
            last_message = chat.messages.last()
            item = {
                "id":
                chat.id,
                "unread_message_quanty":
                unread_chats_dict[chat.id]
                if chat.id in unread_chats_dict else 0,
                "title":
                chat.title,
                "alter_date":
                chat.alter_date
                if not last_message else last_message.create_date,
                "label":
                chat.label,
                "has_messages":
                chat.messages.exists()
            }
            items.append(item)
        unread_chats_ids = list(
            set(
                unread_chats.values_list('message__chat',
                                         flat=True).order_by('-create_date')))
        return sorted(
            items, key=lambda i: i.get('id') in unread_chats_ids, reverse=True)

    def get(self, request, *args, **kwargs):
        users = [request.user.pk]
        users.extend(Team.get_members(request.user))        
        filters = {
            "users__user_by_chat__in": users,
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
            filters["messages__alter_date__gt"] = since

        office = Office.objects.get(pk=office_id)
        chats = office.chats.filter(**filters).distinct('id').prefetch_related(
            'messages').order_by('id')
        data = self.add_count_unread_message(users, chats)
        return JsonResponse(data, safe=False)


class ChatMenssage(View):
    def get(self, request, *args, **kwargs):
        chat = Chat.objects.get(pk=int(request.GET.get('chat')))
        messages = list(
            chat.messages.all().values('message', 'create_user__username',
                                       'create_user_id', 'create_date'))
        office = get_office_session(request)
        if chat.tasks_company_chat.exists():
            task = chat.tasks_company_chat.first()
        else:
            task = chat.task_set.filter(pk=chat.label.split('-')[1]).first()
        if task:
            if task.parent and task.parent.office == office:
                task_id = task.parent.pk
            elif task.get_latest_child_not_refused and task.get_latest_child_not_refused.office == office:
                task_id = task.get_latest_child_not_refused.pk
            else:
                task_id = task.pk
        else:
            task_id = ''
        data = {
            "messages":
            messages,
            "request_user_id":
            request.user.id,
            "chat":
            model_to_dict(
                chat, fields=([field.name for field in chat._meta.fields])),
            "task":
            task_id,
            "status": task.task_status
        }
        return JsonResponse(data, safe=False)


class InternalChatOffices(View):
    def get(self, request, *args, **kwargs):
        task = Task.objects.get(pk=int(request.GET.get('task')))
        data = []
        if task.company_chat:
            data.append({
                'chat':
                task.company_chat.pk,  # "Deve ser o pk da propria task"
                'office_pk':
                task.office.pk,  #"Deve ser o pk do office do parent"
                'name': task.company_chat.company.name,
                'logo': task.company_chat.company.logo.url
            })
        if task.parent:
            data.append({
                'chat': task.chat.pk,  # "Deve ser o pk da propria task"
                'office_pk':
                task.parent.office.pk,  # "Deve ser o pk do office do parent"
                'name': task.parent.office.legal_name
            })
        if task.get_latest_child_not_refused:
            task_child = task.get_latest_child_not_refused
            data.append({
                'chat':
                task_child.chat.pk,  # "Deve ser o pk do chat da task filha"
                'office_pk': task_child.office.pk,
                'name': task_child.office.legal_name
            })
        if task.child.filter(task_status__in=[TaskStatus.REFUSED.value, TaskStatus.REFUSED_SERVICE.value]):
            for task_child in task.child.filter(task_status__in=
                                                [TaskStatus.REFUSED.value, TaskStatus.REFUSED_SERVICE.value]):
                if task_child.chat.messages.all():
                    data.append({
                        'chat':
                            task_child.chat.pk,  # "Deve ser o pk do chat da task filha"
                        'office_pk': task_child.office.pk,
                        'name': task_child.office.legal_name
                    })
        if not any([task.parent, task.get_latest_child_not_refused]):
            data.append({
                'chat': task.chat.pk,  # "Deve ser o pk do chat da task filha"
                'office_pk': task.office.pk,
                'name': task.office.legal_name,
            })
        return JsonResponse(data, safe=False)


class UnreadMessageView(CustomLoginRequiredView, View):
    def post(self, request, *args, **kwargs):
        chat_id = json.loads(request.body).get('chat')
        chat = Chat.objects.get(pk=chat_id)
        chat.save()
        if (chat.messages.exists()):
            user_by_chat = chat.users.filter(user_by_chat=request.user).first()
            unread_message = UnreadMessage.objects.create(
                create_user=request.user,
                message=chat.messages.latest('pk'),
                user_by_message=user_by_chat)
            unread_message.message.save()
        return JsonResponse({'status': 'ok'})
