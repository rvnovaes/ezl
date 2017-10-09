from django.conf.urls import url
from django.conf import settings
# http://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from . import views

urlpatterns = [

    url(r'^ajuda/manual-do-usuario/$',
        RedirectView.as_view(url=settings.USER_MANUAL_URL, permanent=False),
        name='user_manual'),

    url(r'^$', views.login, name='login'),
    url(r'^logout/', views.logout_user, name='logout'),
    url(r'^inicial/', login_required(views.inicial), name='inicial'),
    url(r'^pessoas/listar/$', login_required(views.PersonListView.as_view()), name='person_list'),
    url(r'^pessoas/$', login_required(views.PersonCreateView.as_view()), name='person_add'),
    url(r'^pessoas/(?P<pk>[0-9]+)/$', login_required(views.PersonUpdateView.as_view()), name='person_update'),
    url(r'^pessoas/excluir$', login_required(views.PersonDeleteView.as_view()), name='person_delete'),
    # url(r'^pessoas/endereco/(?P<pk>[0-9]+)/delete$', views.person_address_delete, name='person_address_delete'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/$', views.person_address_information, name='person_address_information'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/atualizar/$', views.address_update, name='address_update'),
    url(r'^pessoas/endereco/pais/$', views.person_address_search_country, name='address_country'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/estado/$', views.person_address_search_state, name='address_state'),
    url(r'^pessoas/endereco/(?P<pk>[0-9]+)/cidade/$', views.person_address_search_city, name='address_city'),
    url(r'^pessoas/endereco/tipo$', views.person_address_search_address_type, name='addresses_types'),
    url(r'^recover_database', views.recover_database, name='recover_database'),

    url(r'^usuarios/listar/$', login_required(views.UserListView.as_view()), name='user_list'),
    url(r'^usuarios/$', login_required(views.UserCreateView.as_view()), name='user_add'),
    url(r'^usuarios/(?P<pk>[0-9]+)/$', login_required(views.UserUpdateView.as_view()), name='user_update'),
    url(r'^usuarios/excluir$', login_required(views.UserDeleteView.as_view()), name='user_delete'),
]
