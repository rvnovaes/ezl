from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()

router.register(r'service_price_table', views.ServicePriceTableViewSet, base_name='service_price_table')

urlpatterns = [

]


