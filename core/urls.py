from django.conf.urls import url
# http://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [

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

]
