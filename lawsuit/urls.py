from django.conf.urls import url, include

from lawsuit import views

urlpatterns = [
    # url(r'^tipo-movimentacao/listar$', views.type_movement_list, name='type_movement_list'),
    url(r'^tipo-movimentacao/listar$', views.TypeMovementList.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.type_movement, name='type_movement'),
    # Instances
    url(r'^instancias/$', views.instances, name='instances'),
    url(r'nova_instancia/$', views.instance, name='instance'),
    url(r'apagar/(?P<id_instance>[0-9]+)/', views.delete_instance, name='delete_instance')

]