from django.conf.urls import url , include

from lawsuit import views

urlpatterns = [

    #Tipo de movimentacao
    url(r'^tipo-movimentacao/listar/$', views.TypeMovementListView.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.TypeMovementCreateView.as_view(), name='type_movement_add'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/$', views.TypeMovementUpdateView.as_view(), name='type_movement_update'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/excluir$', views.TypeMovementDeleteView.as_view(),
        name='type_movement_delete'),

    url(r'^instancias/$', views.instances, name='instances'),
    url(r'nova_instancia/$', views.instance, name='instance'),
    url(r'apagar/(?P<id_instance>[0-9]+)/', views.delete_instance, name='delete_instance')

]