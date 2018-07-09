from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views


router = routers.SimpleRouter()
router.register(r'persons', views.PersonViewSet, base_name='persons')

urlpatterns = []