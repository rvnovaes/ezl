from django.views.generic import ListView
from chat.models import Chat


class ChatListView(ListView):
    model = Chat


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['chats'] = Chat.objects.filter(label='teste-1')
        context['chats'] = Chat.objects.all()
        return context
