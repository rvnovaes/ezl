from django.views.generic import ListView
from chat.models import Chat, UnreadMessage
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
