from django.conf.urls import url, include

from lawsuit import views
from lawsuit.views import TemplateView

urlpatterns = [
    url(r'^tipo-movimentacao/listar$', views.TypeMovementList.as_view(), name='type_movement_list'),
    url(r'^tipo-movimentacao/$', views.type_movement, name='type_movement'),
    # Instances
    #url(r'^instancias/$', views.instances, name='instances'),
    url(r'^instancias/$', TemplateView.as_view()),
    url(r'nova_instancia/$', views.instance, name='instance'),
    url(r'apagar/(?P<id_instance>[0-9]+)/', views.delete_instance, name='delete_instance')

]