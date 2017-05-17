from django.conf.urls import url, include

from lawsuit import views

urlpatterns = [
    url(r'^tipo-movimentacao/listar$', views.TypeMovementList.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.type_movement, name='type_movement'),
    # Instances
    #url(r'^instancias/$', views.instances, name='instances'),
    url(r'^instancias/listar/$', views.InstanceListView.as_view(), name='instance_list'),
    url(r'instancias/$', views.InstanceCreateView.as_view(), name='instance_create'),
    url(r'instancias/(?P<pk>[0-9]+)/$', views.InstanceUpdateView.as_view(), name='instance_update')

]