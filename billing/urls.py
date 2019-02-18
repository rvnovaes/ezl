from django.conf.urls import url
from billing import views

urlpatterns = [
    url(r'^charge/$', views.ChargeCreateView.as_view(), name='charge_create'),    
    url(r'^confirm_payment/$', views.ConfirmPayment.as_view(), name='confirm_payment'),
    url(r'^detail_payment/(?P<charge_id>[0-9]+)/$', views.DetailPayment.as_view(), name='detail_payment'),
    url(r'^create_billing_detail/$', views.BillingDetailAjaxCreate.as_view(), name='create_billing_detail'),
    url(r'^update_billing_detail/(?P<pk>[0-9]+)/$', views.BillingDetailAjaxUpdate.as_view(),
        name='create_billing_detail'),
    url(r'^get_billing_detail/(?P<pk>[0-9]+)/$', views.BillingDetailDataView.as_view(), name='get_billing_detail'),
    url(r'^delete_billing_detail/$', views.BillingDetailAjaxDelete.as_view(), name='delete_billing_detail'),
    url(r'^get_office_billing_detail/$', views.BillingDetailByOffice.as_view(), name='get_office_billing_detail'),
]
