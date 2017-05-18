from django.conf.urls import url, include

from lawsuit import views

urlpatterns = [

    #Tipo de movimentacao
    url(r'^tipo-movimentacao/listar/$', views.TypeMovementListView.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.TypeMovementCreateView.as_view(), name='type_movement_add'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/$', views.TypeMovementUpdateView.as_view(), name='type_movement_update'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/excluir$', views.TypeMovementDeleteView.as_view(), name='type_movement_delete'),

    #url(r'^instancias/$', views.instances, name='instances'),
    url(r'^instancias/listar/$', views.InstanceListView.as_view(), name='instance_list'),
    url(r'instancias/$', views.InstanceCreateView.as_view(), name='instance_create'),
    url(r'instancias/(?P<pk>[0-9]+)/$', views.InstanceUpdateView.as_view(), name='instance_update')

]