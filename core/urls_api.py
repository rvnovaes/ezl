from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()
router.register(r'person', views.PersonViewSet, base_name='person')
router.register(r'company', views.CompanyViewSet, base_name='company')

urlpatterns = [url(r'^user_session/$', views.user_session_view)]
