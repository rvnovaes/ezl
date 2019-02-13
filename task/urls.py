from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.conf import settings
from task import views

urlpatterns = [
    # Providências
    url(r'^{}(?P<path>.*)/(?P<task_hash>[-\w\W\d]+)/$'.format(settings.MEDIA_URL.lstrip('/')),
        views.ExternalMediaFileView.as_view(),
        name='external-media'),    
    url(r'^providencias/listar/$',
        login_required(views.TaskListView.as_view()),
        name='task_list'),
    url(r'^providencias/(?P<movement>[0-9]+)/criar/$',
        login_required(views.TaskCreateView.as_view()),
        name='task_add'),
    url(r'^providencias/(?P<movement>[0-9]+)/(?P<pk>[0-9]+)/$',
        login_required(views.TaskUpdateView.as_view()),
        name='task_update'),
    url(r'^(?P<pk>[0-9]+)/atribuir$',
        login_required(views.TaskToAssignView.as_view()),
        name='task_to_assign'),
    url(r'^(?P<pk>[0-9]+)/batch/recusar$',
        login_required(views.BatchTaskToRefuseView.as_view()),
        name='batch_task_to_refuse'),    
    url(r'^(?P<pk>[0-9]+)/batch/atribuir$',
        login_required(views.BatchTaskToAssignView.as_view()),
        name='batch_task_to_assign'),
    url(r'^(?P<pk>[0-9]+)/batch/delegar$',
        login_required(views.BatchTaskToDelegateView.as_view()),
        name='batch_task_to_delegate'),        
    url(r'^batch/service_price_table$',
        login_required(views.BatchServicePriceTable.as_view()),
        name='batch_service_price_table'),         
    url(r'^(?P<pk>[0-9]+)/batch/batch_cheapest_correspondent$',
        login_required(views.BatchCheapestCorrespondent.as_view()),
        name='batch_cheapest_correspondent'),               
    url(r'^providencias/excluir$',
        login_required(views.TaskDeleteView.as_view()),
        name='task_delete'),
    url(r'^providencias/geolocation/checkin',
        login_required(views.GeolocationTaskCreate.as_view()),
        name='task_geolocation_create'),
    url(r'^providencias/geolocation/finalizar$',
        login_required(views.GeolocationTaskFinish.as_view()),
        name='task_geolocation_finish'),
    url(r'^task/update/amount$', 
        login_required(views.TaskUpdateAmountView.as_view()), 
        name='task_update_amount'),
    url(r'^ecm/(?P<pk>[0-9]+)/$',
        views.EcmCreateView.as_view(),
        name='ecm_add'),
    url(r'^ecm/(?P<pk>[0-9]+)/excluir$', views.delete_internal_ecm, name='delete_ecm'),
    url(r'^ecm/(?P<task_hash>[-\w\W\d]+)/(?P<pk>[0-9]+)/excluir$', views.delete_external_ecm, name='delete_external_ecm'),
    url(r'^ecm/ecm_batch_download/(?P<pk>[0-9]+)/$',
        views.ecm_batch_download,
        name='ecm_batch_download'),
    url(r'^ajax_get_task_data_table/$',
        login_required(views.ajax_get_task_data_table),
        name='ajax_get_task_data_table'),
    url(r'^ajax_get_ecms/$',
        login_required(views.ajax_get_ecms),
        name='ajax_get_ecms'),
    url(r'^ajax_get_external_ecms/$',
        views.get_external_ecms,
        name='ajax_get_external_ecms'),
    url(r'^ajax_get_correspondent_table/$',
        login_required(views.ajax_get_correspondents_table),
        name='ajax_get_correspondent_table'),
    url(r'^ajax_bulk_create_update_status/$',
        login_required(views.ajax_bulk_create_update_status),
        name='ajax_bulk_create_update_status'),

    # Filtros
    url(r'^filtros/listar/$',
        login_required(views.FilterListView.as_view()),
        name='filter_list'),
    url(r'^filtros/(?P<pk>[0-9]+)/$',
        login_required(views.FilterUpdateView.as_view()),
        name='filter_update'),
    url(r'^filtros/excluir$',
        login_required(views.FilterDeleteView.as_view()),
        name='filter_delete'),
    url(r'^external-task/(?P<status>[A-Z]+)/(?P<task_hash>[-\w\W\d]+)/$',
        views.ExternalTaskView.as_view(),
        name="external-task"),
    url(r'^external-task/ecm/(?P<task_hash>[-\w\W\d]+)/$',
        views.EcmExternalCreateView.as_view(),
        name='ecm_external_add'),
    url(r'^external-task-detail/(?P<task_hash>[-\w\W\d]+)/$',
        views.ExternalTaskView.as_view(),
        name="external-task-detail"),

    # TypeTask
    url(r'^type_task/listar/$',
        login_required(views.TypeTaskListView.as_view()),
        name='typetask_list'),
    url(r'^type_task/criar/$',
        views.TypeTaskCreateView.as_view(),
        name='typetask_add'),
    url(r'^type_task/(?P<pk>[0-9]+)/$',
        login_required(views.TypeTaskUpdateView.as_view()),
        name='typetask_update'),
    url(r'^type_task/excluir$',
        login_required(views.TypeTaskDeleteView.as_view()),
        name='typetask_delete'),
    url(r'^type_task_main/(?P<pk>[0-9]+)/get$',
        login_required(views.GetTypeTaskMainCharacteristics.as_view()),
        name='typetaskmain_get'),

    url(r'^batch_change_tasks/(?P<option>[A-Z]+)/', login_required(views.BatchChangeTasksView.as_view()), 
        name='batch_change_tasks'),

    url(r'^task_to_company_representative/$', login_required(views.ViewTaskToPersonCompanyRepresentative.as_view()), 
        name="task_to_company_representative"),

    # Filtros
    url(r'^import_task_list/$',
        login_required(views.ImportTaskList.as_view()),
        name='import_task_list'),
    url(r'^type-task-autocomplete/$', views.TypeTaskAutocomplete.as_view(), name='type-task-autocomplete'),
    url(r'^type-task-main-autocomplete/$', views.TypeTaskMainAutocomplete.as_view(), name='type-task-main-autocomplete'),

    # Relatórios
    url(r'^task_checkin_report/$',
        login_required(views.TaskCheckinReportView.as_view()),
        name='task_checkin_report'),
]
