from django.conf.urls import url, include

from lawsuit import views

urlpatterns = [

    # Processos
    url(r'^processos/listar/$', views.LawSuitListView.as_view(), name='lawsuit_list'),
    url(r'^processos/$', views.LawSuitCreateView.as_view(), name='lawsuit_add'),
    url(r'^processos/(?P<pk>[0-9]+)/$', views.LawSuitUpdateView.as_view(), name='lawsuit_update'),
    url(r'^processos/(?P<pk>[0-9]+)/excluir$', views.LawSuitDeleteView.as_view(),
        name='movement_delete'),

    # Movimentacao
    url(r'^movimentacao/listar/$', views.MovementListView.as_view(), name='movement_list'),
    url(r'^movimentacao/$', views.MovementCreateView.as_view(), name='movement_add'),
    url(r'^movimentacao/(?P<pk>[0-9]+)/$', views.MovementUpdateView.as_view(), name='movement_update'),
    url(r'^movimentacao/(?P<pk>[0-9]+)/excluir$', views.MovementDeleteView.as_view(),
        name='movement_delete'),

    # Tipo de movimentacao
    url(r'^tipo-movimentacao/listar/$', views.TypeMovementListView.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.TypeMovementCreateView.as_view(), name='type_movement_add'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/$', views.TypeMovementUpdateView.as_view(), name='type_movement_update'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/excluir$', views.TypeMovementDeleteView.as_view(),
        name='type_movement_delete'),

    # Intancias
    url(r'^instancias/listar/$', views.InstanceListView.as_view(), name='instance_list'),
    url(r'instancias/$', views.InstanceCreateView.as_view(), name='instance_create'),
    url(r'instancias/(?P<pk>[0-9]+)/$', views.InstanceUpdateView.as_view(), name='instance_update'),
    url(r'^instancias/(?P<pk>[0-9]+)/excluir/$', views.InstanceDeleteView.as_view(), name='instance_delete')

]