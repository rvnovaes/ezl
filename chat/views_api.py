from rest_framework import viewsets
from .serializers import ChatSerializer, UnreadMessageSerializer
from .models import Chat, UnreadMessage
from django_filters.rest_framework import DjangoFilterBackend


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('company', )


class UnreadMessageViewSet(viewsets.ModelViewSet):
    queryset = UnreadMessage.objects.all().order_by('message__chat__tasks_company_chat__final_deadline_date', '-message_id')
    serializer_class = UnreadMessageSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('user_by_message__user_by_chat_id', 'message__message', 'message__chat__company_id')

    # def get_queryset(self):
    #     user = self.request.user
    #     return UnreadMessage.objects.filter(
    #         user_by_message__user_by_chat_id=user.pk).order_by('-id')
