from django.conf.urls import url, include

from lawsuit import  views
urlpatterns = [
    url(r'^cadastro-tipo-movimentacao/$', views.type_movement_list,name='type_movements'),
    url(r'^cadastro-tipo-movimentacao/(?P<type_movement_id>\d+)/$', views.type_movement_crud, name='type_movement'),
    # Instances
    url(r'^instancias/$', views.instances, name='instances'),
    url(r'nova_instancia/$', views.instance, name='instance'),
    url(r'apagar/(?P<id_instance>[0-9]+)/', views.delete_instance, name='delete_instance')

]