from django.conf.urls import url, include

from lawsuit import views

urlpatterns = [
    # url(r'^tipo-movimentacao/listar$', views.type_movement_list, name='type_movement_list'),
    url(r'^tipo-movimentacao/listar$', views.TypeMovementList.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.type_movement, name='type_movement'),


]