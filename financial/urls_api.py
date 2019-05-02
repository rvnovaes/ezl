from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()

router.register(r'service_price_table', views.ServicePriceTableViewSet, base_name='service_price_table')
router.register(r'cost_center', views.CostCenterViewSet, base_name='cost_center')
router.register(r'policy_price', views.PolicyPriceViewSet, base_name='policy_price')

urlpatterns = [

]


