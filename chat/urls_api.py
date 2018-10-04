from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()
router.register(r'chat', views.ChatViewSet, base_name='chat')
router.register(
    r'unread_message', views.UnreadMessageViewSet, base_name='unread_message')

urlpatterns = []
