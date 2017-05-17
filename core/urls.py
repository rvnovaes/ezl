from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^$', views.login, name='login'),
    url(r'^pessoas/listar$', views.PersonListView.as_view(), name='person_list'),
    url(r'^pessoas/$', views.PersonCreateView.as_view(), name='person_add'),
    url(r'^pessoas/(?P<pk>[0-9]+)/$', views.PersonUpdateView.as_view(), name='person_update'),
    url(r'^pessoas/(?P<pk>[0-9]+)/excluir$', views.PersonDeleteView.as_view(), name='person_delete')
]
