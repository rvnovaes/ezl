from django.conf.urls import url, include

from lawsuit import  views
urlpatterns = [
    url(r'^type_movements/$', views.type_movement_list,name='type_movements'),
    url(r'^cadastro-tipo-movimentacao/(?P<type_movement_id>\d+)/$', views.type_movement_crud, name='type_movement'),
    # Instances
    url(r'^instancias/$', views.instance, name='instance'),
    url(r'nova_instancia/$', views.nova_instancia, name='nova_instance'),
    url(r'apagar/(?P<id_instance>[0-9]+)/', views.delete_instance, name='delete_instance')

]