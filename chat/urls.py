from django.conf.urls import url
from chat import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='chat_list'),
    url(r'^count_message/$', views.ChatCountMessages.as_view(), name='chat_count_message'),
    url(r'^chat_read_messages$', views.ChatReadMessages.as_view(), name='chat_read_message'),
    url(r'^chat_get_messages$', views.ChatGetMessages.as_view(), name='chat_get_message'),
    url(r'^chat_unread_messages/$', views.ChatMarkMessagesUnread.as_view(), name='chat_unread_message'),
]
