from django.conf.urls import url, include
from rest_framework import routers
from . import views_api as views


router = routers.SimpleRouter()
router.register(r'dashboard', views.DashboardViewSet, base_name='dashboard')

urlpatterns = [
	
]