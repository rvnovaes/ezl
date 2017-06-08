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
    url(r'^pessoas/excluir$', login_required(views.PersonDeleteView.as_view()), name='person_delete')
]
