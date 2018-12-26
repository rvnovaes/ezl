from django.conf.urls import url
from billing import views

urlpatterns = [
    url(r'^charge/$', views.ChargeCreateView.as_view(), name='charge_create'),    
]
