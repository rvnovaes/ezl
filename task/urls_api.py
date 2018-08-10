from django.conf.urls import url, include
from rest_framework import routers
from . import views_api as views


router = routers.SimpleRouter()
router.register(r'type_task', views.TypeTaskViewSet, base_name='type_task')
router.register(r'task', views.TaskViewSet, base_name='task')
router.register(r'ecm_task', views.EcmTaskViewSet, base_name='task')

urlpatterns = [
	url(r'^audience/$', views.list_audience_totals)
]