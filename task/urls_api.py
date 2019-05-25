from django.conf.urls import url, include
from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()
router.register(r'type_task', views.TypeTaskViewSet, base_name='type_task')
router.register(r'type_task_main', views.TypeTaskMainViewSet, base_name='type_task_main')
router.register(r'task', views.TaskViewSet, base_name='task')
router.register(r'task_dashboard', views.TaskDashboardEZLViewSet, base_name='task_dashboard')
router.register(r'total_by_office', views.TotalToPayByOfficeViewSet, base_name='total_by_office')
router.register(r'task_to_pay', views.TaskToPayViewSet, base_name='task_to_pay')
router.register(r'tasks_child', views.ChildTaskToPayViewSet, base_name='tasks_child')
router.register(r'ecm_task', views.EcmTaskViewSet, base_name='task')

urlpatterns = [url(r'^audience/$', views.list_audience_totals)]
