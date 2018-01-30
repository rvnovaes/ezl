from django.views.generic import ListView
from chat.models import Chat, UnreadMessage, Message
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View
from django.db.models import Count
import json


class ChatListView(ListView):
    model = Chat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['chats'] = Chat.objects.all()
        else:
            context['chats'] = Chat.objects.filter(users__user_by_chat=self.request.user).order_by(
                'pk').distinct('pk')
        return context


class ChatCountMessages(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {'all_messages': UnreadMessage.objects.filter(
                user_by_message__user_by_chat=self.request.user).count(),
             'grouped_messages': list(UnreadMessage.objects.filter(
                 user_by_message__user_by_chat=self.request.user).values(
                 'message__chat__pk').annotate(
                 quantity=Count('id')).order_by())
             }
        )


class ChatReadMessages(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        chat_id = request.POST.get('chat_id')
        chat = Chat.objects.filter(pk=int(chat_id)).first()
        if chat:
            UnreadMessage.objects.filter(user_by_message__user_by_chat=self.request.user,
                                         message__chat=chat).delete()
        return JsonResponse({'status': 'ok'})


class ChatGetMessages(LoginRequiredMixin, View):
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
                'message_create_date': x.create_date.strftime("%d-%m-%Y às %H:%M:%S"),
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
        print('*****', data)
        return JsonResponse(data)
