from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from lawsuit import views


urlpatterns = [

    # Comarcas
    url(r'^comarcas/listar/$', login_required(views.CourtDistrictListView.as_view()), name='courtdistrict_list'),
    url(r'^comarcas/$', login_required(views.CourtDistrictCreateView.as_view()), name='courtdistrict_add'),
    url(r'^comarcas/(?P<pk>[0-9]+)/$', login_required(views.CourtDistrictUpdateView.as_view()),
        name='courtdistrict_update'),
    url(r'^comarcas/excluir$', login_required(views.CourtDistrictDeleteView.as_view()),
        name='courtdistrict_delete'),
    url(r'courtdistrict_autocomplete$', login_required(views.CourtDistrictAutocomplete.as_view()),
        name='courtdistrict_autocomplete'),

    # Varas
    url(r'^varas/listar/$', login_required(views.CourtDivisionListView.as_view()), name='courtdivision_list'),
    url(r'^varas/$', login_required(views.CourtDivisionCreateView.as_view()), name='courtdivision_add'),
    url(r'^varas/(?P<pk>[0-9]+)/$', login_required(views.CourtDivisionUpdateView.as_view()),
        name='courtdivision_update'),
    url(r'^varas/excluir$', login_required(views.CourtDivisionDeleteView.as_view()),
        name='courtdivision_delete'),

    # Processos
    url(r'^processos/listar/$', login_required(views.LawSuitListView.as_view()), name='lawsuit_list'),
    url(r'^processos/(?P<folder>[0-9]+)/$', login_required(views.LawsuitMovementCreateView.as_view()),
        name='lawsuit_add'),
    url(r'^processos/(?P<folder>[0-9]+)/(?P<pk>[0-9]+)/$', login_required(views.LawsuitMovementUpdateView.as_view()),
        name='lawsuit_update'),
    url(r'^processos/excluir$', login_required(views.LawSuitDeleteView.as_view()),
        name='lawsuit_delete'),

    # Movimentacao
    url(r'^movimentacao/listar/$', login_required(views.MovementListView.as_view()), name='movement_list'),
    url(r'^movimentacao/(?P<lawsuit>[0-9]+)$', login_required(views.MovementTaskCreateView.as_view()),
        name='movement_add'),
    url(r'^movimentacao/(?P<lawsuit>[0-9]+)/(?P<pk>[0-9]+)/$', login_required(views.MovementTaskUpdateView.as_view()),
        name='movement_update'),
    url(r'^movimentacao/excluir$', login_required(views.MovementDeleteView.as_view()),
        name='movement_delete'),

    # Tipo de movimentacao
    url(r'^tipo-movimentacao/listar/$', login_required(views.TypeMovementListView.as_view()),
        name='type_movement_list'),
    url(r'^tipo-movimentacao/$', login_required(views.TypeMovementCreateView.as_view()), name='type_movement_add'),
    url(r'^tipo-movimentacao/(?P<pk>[0-9]+)/$', login_required(views.TypeMovementUpdateView.as_view()),
        name='type_movement_update'),
    url(r'^tipo-movimentacao/excluir$', login_required(views.TypeMovementDeleteView.as_view()),
        name='type_movement_delete'),

    # Intancias
    url(r'^instancias/listar/$', login_required(views.InstanceListView.as_view()), name='instance_list'),
    url(r'instancias/$', login_required(views.InstanceCreateView.as_view()), name='instance_create'),
    url(r'instancias/(?P<pk>[0-9]+)/$', login_required(views.InstanceUpdateView.as_view()), name='instance_update'),
    url(r'instancias/excluir$', login_required(views.InstanceDeleteView.as_view()),
        name='instance_delete'),

    # PastasSolicitante
    url(r'^pastas/listar/$', login_required(login_required(views.FolderListView.as_view())), name='folder_list'),
    url(r'^pastas/$', login_required(login_required(views.FolderLawsuitCreateView.as_view())), name='folder_add'),
    url(r'^pastas/(?P<pk>[0-9]+)/$', login_required(login_required(views.FolderLawsuitUpdateView.as_view())),
        name='folder_update'),
    url(r'^pastas/excluir$', login_required(login_required(views.FolderDeleteView.as_view())),
        name='folder_delete'),

    # Orgao
    url(r'^orgaos/listar/$', login_required(views.OrganListView.as_view()), name='organ_list'),
    url(r'^orgaos/$', login_required(views.OrganCreateView.as_view()), name='organ_add'),
    url(r'^orgaos/(?P<pk>[0-9]+)/$', login_required(views.OrganUpdateView.as_view()),
        name='organ_update'),
    url(r'orgaos/excluir$', login_required(views.OrganDeleteView.as_view()), name='organ_delete'),
    url(r'organ_autocomplete$', login_required(views.OrganAutocompleteView.as_view()),
        name='organ_autocomplete'),

    # Address views
    url(r'^orgaos/(?P<person_pk>[0-9]+)/enderecoes/criar/$', views.AddressOrganCreateView.as_view(),
        name='address_organ_create'),

    url(r'^orgaos/(?P<person_pk>[0-9]+)/enderecoes/(?P<pk>[0-9]+)/$',
        views.AddressOrganUpdateView.as_view(),
        name='address_organ_update'),

    url(r'^orgaos/(?P<person_pk>[0-9]+)/enderecoes/(?P<pk>[0-9]+)/excluir/$',
        views.AddressOrganDeleteView.as_view(),
        name='address_organ_delete'),
]
