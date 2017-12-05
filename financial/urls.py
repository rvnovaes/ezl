from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^centros-de-custos/$', views.CostCenterListView.as_view(), name='costcenter_list'),
    url(r'^centros-de-custos/criar/$', views.CostCenterCreateView.as_view(), name='costcenter_add'),
    url(r'^centros-de-custos/(?P<pk>[0-9]+)/$', views.CostCenterUpdateView.as_view(), name='costcenter_update'),
    url(r'^centros-de-custos/excluir$', views.CostCenterDeleteView.as_view(), name='costcenter_delete'),
    url(r'^centros-de-custos/autocomplete', views.CostCenterAutocomplete.as_view(), name='costcenter_autocomplete'),
]
