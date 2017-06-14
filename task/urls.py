from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from task import views

urlpatterns = [
    # Providências
    url(r'^providencias/listar/$', login_required(views.TaskListView.as_view()), name='task_list'),
    url(r'^providencias/$', login_required(views.TaskCreateView.as_view()), name='task_add'),
    url(r'^providencias/(?P<pk>[0-9]+)/$', login_required(views.TaskUpdateView.as_view()), name='task_update'),
    url(r'^providencias/(?P<pk>[0-9]+)/excluir$', login_required(views.TaskDeleteView.as_view()),
        name='task_delete'),
    url(r'^ecm/(?P<pk>[0-9]+)/$', login_required(views.EcmCreateView.as_view()), name='ecm_add')
]
