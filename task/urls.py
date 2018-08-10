from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from task import views

urlpatterns = [
    # Providências
    url(r'^providencias/listar/$', login_required(views.TaskListView.as_view()), name='task_list'),

    url(r'^providencias/(?P<movement>[0-9]+)/criar/$',
        login_required(views.TaskCreateView.as_view()), name='task_add'),

    url(r'^providencias/(?P<movement>[0-9]+)/(?P<pk>[0-9]+)/$',
        login_required(views.TaskUpdateView.as_view()),
        name='task_update'),
    url(r'^(?P<pk>[0-9]+)/atribuir$',
        login_required(views.TaskToAssignView.as_view()), name='task_to_assign'),
    url(r'^providencias/excluir$', login_required(views.TaskDeleteView.as_view()),
        name='task_delete'),

    url(r'^providencias/geolocation/checkin', login_required(views.GeolocationTaskCreate.as_view()),
        name='task_geolocation_create'),

    url(r'^providencias/geolocation/finalizar$', login_required(views.GeolocationTaskFinish.as_view()),
        name='task_geolocation_finish'),

    url(r'^ecm/(?P<pk>[0-9]+)/$', login_required(views.EcmCreateView.as_view()), name='ecm_add'),

    url(r'^ecm/(?P<pk>[0-9]+)/excluir$', views.delete_ecm, name='delete_ecm'),

    url(r'^ecm/ecm_batch_download/(?P<pk>[0-9]+)/$', views.ecm_batch_download, name='ecm_batch_download'),

    url(r'^ajax_get_task_data_table/$', login_required(views.ajax_get_task_data_table),
        name='ajax_get_task_data_table'),
    url(r'^ajax_get_ecms/$', login_required(views.ajax_get_ecms),
        name='ajax_get_ecms'),

    # Filtros
    url(r'^filtros/listar/$',
        login_required(views.FilterListView.as_view()),
        name='filter_list'),

    url(r'^filtros/(?P<pk>[0-9]+)/$', login_required(views.FilterUpdateView.as_view()),
        name='filter_update'),

    url(r'^filtros/excluir$', login_required(views.FilterDeleteView.as_view()),
        name='filter_delete'),

    # Filtros
    url(r'^import_task_list/$',
        login_required(views.ImportTaskList.as_view()),
        name='import_task_list'),

]
