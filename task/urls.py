from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from task import views

urlpatterns = [
    # Providências
    url(r'^providencias/listar/$', login_required(views.TaskListView.as_view()), name='task_list'),
    url(r'^providencias/(?P<movement>[0-9]+)/$', login_required(views.TaskCreateView.as_view()), name='task_add'),
    url(r'^providencias/(?P<movement>[0-9]+)/(?P<pk>[0-9]+)/$', login_required(views.TaskUpdateView.as_view()),
        name='task_update'),
    url(r'^providencias/excluir$', login_required(views.TaskDeleteView.as_view()),
        name='task_delete'),
    url(r'^ecm/(?P<pk>[0-9]+)/$', login_required(views.EcmCreateView.as_view()), name='ecm_add'),
    url(r'^ecm/(?P<pk>[0-9]+)/excluir$', views.delete_ecm, name='delete_ecm'),


    # TipoServico
    url(r'^tipo_servico/listar/$', login_required(views.TypeTaskListView.as_view()), name='typetask_list'),
    url(r'^tipo_servico/$', login_required(views.TypeTaskCreateView.as_view()), name='typetask_add'),
    url(r'^tipo_servico/(?P<pk>[0-9]+)/$', login_required(views.TypeTaskUpdateView.as_view()),
        name='typetask_update'),
    url(r'^tipo_servico/excluir$', login_required(views.TypeTaskDeleteView.as_view()),
        name='typetask_delete'),

]
