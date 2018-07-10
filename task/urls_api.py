from django.conf.urls import url, include
from rest_framework import routers
from . import views_api as views


router = routers.SimpleRouter()
router.register(r'type_task', views.TypeTaskViewSet, base_name='type_task')

urlpatterns = []