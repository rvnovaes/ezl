from django.conf.urls import url
from chat import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='chat_list'),
    url(r'^count_message/$', views.ChatCountMessages.as_view(), name='chat_count_message'),
]
