from django.conf.urls import url
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from . import views

urlpatterns = [

    url(r'city/autocomplete/$',
        login_required(views.CityAutoCompleteView.as_view()),
        name='city_autocomplete'),

    url(r'^ajuda/manual-do-usuario/$',
        RedirectView.as_view(url=settings.USER_MANUAL_URL, permanent=False),
        name='user_manual'),

    url(r'^$', views.login, name='login'),
    url(r'^registrar/', views.RegisterNewUser.as_view(), name='register_user'),
    url(r'^logout/', views.logout_user, name='logout'),
    url(r'^inicial/', login_required(views.inicial), name='inicial'),
    url(r'^start/$', login_required(views.StartUserView.as_view()), name='start_user'),
    url(r'^session/$', login_required(views.CustomSession.as_view()),
    name='session'),
    url(r'^users_to_invite/$', login_required(views.ListUsersToInviteView.as_view()),
    name='users_to_invite'),

    # Address views
    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/criar/$',
        views.AddressCreateView.as_view(),
        name='address_create'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/(?P<pk>[0-9]+)/$',
        views.AddressUpdateView.as_view(),
        name='address_update'),

    url(r'^pessoas/(?P<person_pk>[0-9]+)/enderecos/excluir/$',
        views.AddressDeleteView.as_view(),
        name='address_delete'),

    # Person views
    url(r'^pessoas/$', views.PersonListView.as_view(), name='person_list'),
    url(r'^pessoas/criar/$', views.PersonCreateView.as_view(), name='person_add'),
    url(r'^pessoas/(?P<pk>[0-9]+)/$', views.PersonUpdateView.as_view(), name='person_update'),
    url(r'^pessoas/excluir$', views.PersonDeleteView.as_view(), name='person_delete'),

    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/$', views.person_address_information,
        name='person_address_information'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/atualizar/$', views.address_update,
        name='address_update'),
    url(r'^pessoas/endereco/pais/$', views.person_address_search_country, name='address_country'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/estado/$', views.person_address_search_state,
        name='address_state'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/cidade/$', views.person_address_search_city,
        name='address_city'),
    url(r'^pessoas/endereco/tipo$', views.person_address_search_address_type,
        name='addresses_types'),
    url(r'^recover_database', views.recover_database, name='recover_database'),

    url(r'^usuarios/listar/$', login_required(views.UserListView.as_view()), name='user_list'),
    url(r'^usuarios/$', login_required(views.UserCreateView.as_view()), name='user_add'),
    url(r'^usuarios/(?P<pk>[0-9]+)/$', login_required(views.UserUpdateView.as_view()),
        name='user_update'),
    url(r'^usuarios/excluir$', login_required(views.UserDeleteView.as_view()),
        name='user_delete'),
    url(r'^escritorios/$', login_required(views.OfficeListView.as_view()), name='office_list'),
    url(r'^escritorios/excluir$', login_required(views.OfficeDeleteView.as_view()), name='office_delete'),
    url(r'^escritorios/(?P<pk>[0-9]+)/$', views.OfficeUpdateView.as_view(), name='office_update'),
    url(r'^escritorios/criar$', login_required(views.OfficeCreateView.as_view()), name='office_add'),
    url(r'^convites/criar$', login_required(views.InviteCreateView.as_view()), name='invite_add'),
    url(r'^convites/invite_update/$', login_required(views.InviteUpdateView.as_view()), name='invite_update'),
    url(r'^convites/convidar$', login_required(views.InviteMultipleUsersView.as_view()), name='invite_multiple_users')
]
