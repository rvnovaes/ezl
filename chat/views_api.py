from rest_framework import viewsets
from .serializers import ChatSerializer, UnreadMessageSerializer
from .models import Chat, UnreadMessage
from django_filters.rest_framework import DjangoFilterBackend


class ChatViewSet(viewsets.ModelViewSet):
	queryset = Chat.objects.all()
	serializer_class = ChatSerializer
	filter_backends = (DjangoFilterBackend,)
	filter_fields = ('company', )


class UnreadMessageViewSet(viewsets.ModelViewSet):	
	queryset = UnreadMessage.objects.all()
	serializer_class = UnreadMessageSerializer
	filter_backends = (DjangoFilterBackend,)
	filter_fields = ('user_by_message__user_by_chat_id', 'message__message')

	def get_queryset(self):
		user = self.request.user				
		return UnreadMessage.objects.filter(user_by_message__user_by_chat_id=2).order_by('-id')