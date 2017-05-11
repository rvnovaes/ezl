from django.conf.urls import url, include

from lawsuit import  views
urlpatterns = [
    #url(r'^type_movements/$', views.type_movements,name='type_movements'),
    url(r'^cadastro-tipo-movimentacao/(?P<type_movement_id>\d+)/$', views.type_movement_crud, name='type_movement'),


]