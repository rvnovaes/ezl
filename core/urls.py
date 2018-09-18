from django.conf.urls import url
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'city/autocomplete/$',
        login_required(views.CityAutoCompleteView.as_view()),
        name='city_autocomplete'),
    url(r'^$', views.login, name='login'),
    url(r'^registrar/', views.RegisterNewUser.as_view(), name='register_user'),
    url(r'^logout/', views.logout_user, name='logout'),
    url(r'^inicial/', login_required(views.inicial), name='inicial'),
    url(r'^start/$', login_required(views.StartUserView.as_view()), name='start_user'),
    url(r'^office_instance/$',
        login_required(views.OfficeInstanceView.as_view()), name='office_instance'),
    url(r'^session/$', login_required(views.CustomSession.as_view()),
        name='session'),
    url(r'^users_to_invite/$', login_required(views.ListUsersToInviteView.as_view()),
        name='users_to_invite'),

    # Address views
    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/criar/$',
        views.AddressCreateView.as_view(),
        name='address_create'),
    url(r'^escritorio/(?P<office_pk>[0-9]+)/enderecos/criar/$',
        views.AddressOfficeCreateView.as_view(),
        name='address_office_create'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/(?P<pk>[0-9]+)/$',
        views.AddressUpdateView.as_view(),
        name='address_update'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/enderecos/(?P<pk>[0-9]+)/$',
        views.AddressOfficeUpdateView.as_view(),
        name='address_office_update'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/excluir/$',
        views.AddressDeleteView.as_view(),
        name='address_delete'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/enderecos/excluir/$',
        views.AddressOfficeDeleteView.as_view(),
        name='address_office_delete'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/usuarios/desvincular/$',
        views.OfficeMembershipInactiveView.as_view(),
        name='office_membership_inactive'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/escritorios/desvincular/$',
        views.OfficeOfficesInactiveView.as_view(),
        name='office_offices_inactive'),

    # Person views
    url(r'^pessoas/$', views.PersonListView.as_view(), name='person_list'),
    url(r'^pessoas/criar/$', views.PersonCreateView.as_view(), name='person_add'),
    url(r'^pessoas/(?P<pk>[0-9]+)/$',
        views.PersonUpdateView.as_view(), name='person_update'),
    url(r'^pessoas/excluir$', views.PersonDeleteView.as_view(), name='person_delete'),

    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/$', views.person_address_information,
        name='person_address_information'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/atualizar/$', views.address_update,
        name='address_update'),
    url(r'^pessoas/endereco/pais/$',
        views.person_address_search_country, name='address_country'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/estado/$', views.person_address_search_state,
        name='address_state'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/cidade/$', views.person_address_search_city,
        name='address_city'),
    url(r'^pessoas/endereco/tipo$', views.person_address_search_address_type,
        name='addresses_types'),
    url(r'^recover_database', views.recover_database, name='recover_database'),

    url(r'^usuarios/$', login_required(views.UserListView.as_view()), name='user_list'),
    url(r'^usuarios/criar/$',
        login_required(views.UserCreateView.as_view()), name='user_add'),
    url(r'^usuarios/(?P<pk>[0-9]+)/$', login_required(views.UserUpdateView.as_view()),
        name='user_update'),
    url(r'^usuarios/excluir$', login_required(views.UserDeleteView.as_view()),
        name='user_delete'),
    url(r'^escritorios/$', login_required(views.OfficeListView.as_view()),
        name='office_list'),
    url(r'^escritorios/excluir$',
        login_required(views.OfficeDeleteView.as_view()), name='office_delete'),
    url(r'^escritorios/(?P<pk>[0-9]+)/$',
        views.OfficeUpdateView.as_view(), name='office_update'),
    url(r'^escritorios/criar$',
        login_required(views.OfficeCreateView.as_view()), name='office_add'),
    url(r'^convites/criar$',
        login_required(views.InviteCreateView.as_view()), name='invite_add'),
    url(r'^convites/office/criar$',
        login_required(views.InviteOfficeCreateView.as_view()), name='invite_office_add'),
    url(r'^convites/invite_update/$',
        login_required(views.InviteUpdateView.as_view()), name='invite_update'),
    url(r'^convites/invite_office_update/$',
        login_required(views.InviteOfficeUpdateView.as_view()), name='invite_office_update'),
    url(r'^convites/convidar$', login_required(views.InviteMultipleUsersView.as_view()),
        name='invite_multiple_users'),
    url(r'^convites/table/(?P<office_pk>[0-9]+)/$', login_required(
        views.InviteTableView.as_view()), name='invite_table'),
    url(r'^convites/office/table/(?P<office_pk>[0-9]+)/$', login_required(
        views.InviteOfficeTableView.as_view()), name='invite_office_table'),
    url(r'^convites/verificar/$',
        login_required(views.InviteVerify.as_view()), name='invite_verify'),
    url(r'^typeahead/search$', login_required(views.TypeaHeadGenericSearch.as_view()),
        name='typeahead_search'),
    url(r'^typeahead/search/inviteuser$', login_required(views.TypeaHeadInviteUserSearch.as_view()),
        name='typeahead_invite_user'),
    url(r'^typeahead/search/inviteoffice$', login_required(views.TypeaHeadInviteOfficeSearch.as_view()),
        name='typeahead_invite_office'),
    url(r'^taginput/(?P<office_pk>[0-9]+)/permissions$', login_required(views.TagsInputPermissionsView.as_view()),
        name='taginput_permissions'),
    url(r'^office_session_filter/$', views.OfficeSessionSearch.as_view(),
        name='office_session_filter'),
    url(r'^office_filter/$', views.OfficeSearch.as_view(), name='office_filter'),
    url(r'^validate_password/$', views.ValidatePassword.as_view(),
        name='validate_password'),
    url(r'^validate_username/$', views.ValidateUsername.as_view(),
        name='validate_username'),
    url(r'^validate_email/$', views.ValidateEmail.as_view(), name='validate_email'),

    # Contact mechanism views
    url(r'^pessoas/(?P<person_pk>[0-9]+)/contato/criar/$',
        views.ContactMechanismCreateView.as_view(),
        name='contact_mechanism_create'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/contatos/(?P<pk>[0-9]+)/$',
        views.ContactMechanismUpdateView.as_view(),
        name='contact_mechanism_update'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/contatos/excluir/$',
        views.ContactMechanismDeleteView.as_view(),
        name='contact_mechanism_delete'),

    url(r'^escritorio/(?P<office_pk>[0-9]+)/contato/criar/$',
        views.ContactMechanismOfficeCreateView.as_view(),
        name='contact_mechanism_office_create'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/contatos/(?P<pk>[0-9]+)/$',
        views.ContactMechanismOfficeUpdateView.as_view(),
        name='contact_mechanism_office_update'),

    url(r'^escritorios/(?P<office_pk>[0-9]+)/contatos/excluir/$',
        views.ContactMechanismOfficeDeleteView.as_view(),
        name='contact_mechanism_office_delete'),
    url(r'^teams/$', login_required(views.TeamListView.as_view()), name='team_list'),
    url(r'^teams/create/$',
        login_required(views.TeamCreateView.as_view()), name='team_add'),
    url(r'^teams/(?P<pk>[0-9]+)/$',
        login_required(views.TeamUpdateView.as_view()), name='team_update'),
    url(r'^teams/delete$', login_required(views.TeamDeleteView.as_view()),
        name='team_delete'),
    url(r'^custom_settings/$', login_required(views.CustomSettingsCreateView.as_view()), name='custom_settings_create'),
    url(r'^custtom_settings/(?P<pk>[0-9]+)/$', login_required(views.CustomSettingsUpdateView.as_view()), name='custom_settings_update')
]
