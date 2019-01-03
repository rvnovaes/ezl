from django.conf.urls import url
from billing import views

urlpatterns = [
    url(r'^charge/$', views.ChargeCreateView.as_view(), name='charge_create'),    
    url(r'^confirm_payment/$', views.ConfirmPayment.as_view(), name='confirm_payment'),
    url(r'^detail_payment/(?P<charge_id>[0-9]+)/$', views.DetailPayment.as_view(), name='detail_payment')
]
