from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from lawsuit import views

urlpatterns = [

    # Comarcas
    url(r'^comarcas/listar/$', login_required(views.CourtDistrictListView.as_view()), name='courtdistrict_list'),
    url(r'^comarcas/$', login_required(views.CourtDistrictCreateView.as_view()), name='courtdistrict_add'),
    url(r'^comarcas/(?P<pk>[0-9]+)/$', login_required(views.CourtDistrictUpdateView.as_view()),
        name='courtdistrict_update'),
    url(r'^comarcas/(?P<pk>[0-9]+)/excluir$', login_required(views.CourtDistrictDeleteView.as_view()),
        name='courtdistrict_delete'),

    # Pastas
    url(r'^pastas/listar/$', login_required(login_required(views.FolderListView.as_view())), name='folder_list'),
    url(r'^pastas/$', login_required(login_required(views.FolderCreateView.as_view())), name='folder_add'),
    url(r'^pastas/(?P<pk>[0-9]+)/$', login_required(login_required(views.FolderUpdateView.as_view())),
        name='folder_update'),
    url(r'^pastas/(?P<pk>[0-9]+)/excluir$', login_required(login_required(views.FolderDeleteView.as_view())),
        name='folder_delete'),

    # instancia processo
    url(r'^processos-instancias/listar/$', login_required(views.LawSuitInstanceListView.as_view()),
        name='lawsuitinstance_list'),
    url(r'^processos-instancias/$', login_required(views.LawSuitInstanceCreateView.as_view()),
        name='lawsuitinstance_add'),
    url(r'^processos-instancias/(?P<pk>[0-9]+)/$', login_required(views.LawSuitInstanceUpdateView.as_view()),
        name='lawsuitinstance_update'),
    url(r'^processos-instancias/(?P<pk>[0-9]+)/excluir$', login_required(views.LawSuitInstanceDeleteView.as_view()),
        name='movement_delete'),
    # Processos
    url(r'^processos/listar/$', login_required(views.LawSuitListView.as_view()), name='lawsuit_list'),
    url(r'^processos/$', login_required(views.LawSuitCreateView.as_view()), name='lawsuit_add'),
    url(r'^processos/(?P<pk>[0-9]+)/$', login_required(views.LawSuitUpdateView.as_view()), name='lawsuit_update'),
    url(r'^processos/(?P<pk>[0-9]+)/excluir$', login_required(views.LawSuitDeleteView.as_view()),
        name='movement_delete'),

    # Movimentacao
    url(r'^movimentacao/listar/$', login_required(views.MovementListView.as_view()), name='movement_list'),
    url(r'^movimentacao/$', login_required(views.MovementCreateView.as_view()), name='movement_add'),
    url(r'^movimentacao/(?P<pk>[0-9]+)/$', login_required(views.MovementUpdateView.as_view()), name='movement_update'),
    url(r'^movimentacao/(?P<pk>[0-9]+)/excluir$', login_required(views.MovementDeleteView.as_view()),
        name='movement_delete'),

    # Tipo de movimentacao
    url(r'^tipo-movimentacao/listar/$', login_required(views.TypeMovementListView.as_view()),
        name='type_movement_list'),
    url(r'^tipo-movimentacao/$', login_required(views.TypeMovementCreateView.as_view()), name='type_movement_add'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/$', login_required(views.TypeMovementUpdateView.as_view()),
        name='type_movement_update'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/excluir$', login_required(views.TypeMovementDeleteView.as_view()),
        name='type_movement_delete'),

    # Intancias
    url(r'^instancias/listar/$', login_required(views.InstanceListView.as_view()), name='instance_list'),
    url(r'instancias/$', login_required(views.InstanceCreateView.as_view()), name='instance_add'),
    url(r'instancias/(?P<pk>[0-9]+)/$', login_required(views.InstanceUpdateView.as_view()), name='instance_update'),
    url(r'^instancias/(?P<pk>[0-9]+)/excluir/$', login_required(views.InstanceDeleteView.as_view()),
        name='instance_delete'),
]
