from django.conf.urls import url
from chat import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='chat_list'),
    url(r'^count_message/$', views.ChatCountMessages.as_view(), name='chat_count_message'),
    url(r'^chat_read_messages$', views.ChatReadMessages.as_view(), name='chat_read_message'),
    url(r'^chat_get_messages$', views.ChatGetMessages.as_view(), name='chat_get_message'),
    url(r'^chat_teste$', views.chat_teste, name='chat_teste'),
    url(r'^chat_contacts_test$', views.chat_contacts_test, name='chat_contacts_test'),
    url(r'^contact/$', views.ChatOfficeContactView.as_view(), name="contact"),
    url(r'^chats_by_office/$', views.ChatsByOfficeView.as_view(), name="chat_by_office"),
    url(r'^chat_messages/$', views.ChatMenssage.as_view(), name='chat_messages')

]
