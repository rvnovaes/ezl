from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()

router.register(r'court_district', views.CourtDistrictViewSet, base_name='court_district')
router.register(r'folder', views.FolderViewSet, base_name='folder')
router.register(r'instance', views.InstanceViewSet, base_name='instance')
router.register(r'lawsuit', views.LawSuitViewSet, base_name='lawsuit')
router.register(r'type_movement', views.TypeMovementViewSet, base_name='type_movement')

urlpatterns = [

]


