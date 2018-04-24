from django.views.generic import ListView
from chat.models import Chat, UnreadMessage, Message
from core.views import CustomLoginRequiredView
from django.http import JsonResponse
from django.views.generic import View
from django.db.models import Count, Q
import json
from core.models import Person
from core.models import Office
from core.utils import get_office_session
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import  get_groups_with_perms
from django.shortcuts import render

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
        chat_id = request.POST.get('chat_id')
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
    def get(self, request, *args, **kwargs):
        current_office = get_office_session(request)
        chats = Chat.objects.filter(users__user_by_chat=self.request.user, users__is_active=True).order_by(
            'pk').distinct('pk')
        data = list(Office.objects.filter(~Q(pk=current_office.pk), chats__in=chats,).values('pk', 'legal_name').distinct('pk'))
        return JsonResponse(data, safe=False)


class ChatsByOfficeView(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        office = Office.objects.get(pk=int(request.GET.get('office')))
        chats = office.chats.filter(users__user_by_chat=self.request.user, users__is_active=True)
        data = list(chats.values())
        return JsonResponse(data, safe=False)

class ChatMenssage(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        chat = Chat.objects.get(pk=int(request.GET.get('chat')))
        messages = list(chat.messages.all().values('message', 'create_user__username', 'create_user_id', 'create_date'))
        data = {
            "messages": messages,
            "request_user_id": request.user.id
        }
        return  JsonResponse(data, safe=False)
