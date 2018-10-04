from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views

router = routers.SimpleRouter()

router.register(
    r'court_district', views.CourtDistrictViewSet, base_name='court_district')
router.register(r'folder', views.FolderViewSet, base_name='folder')
router.register(r'instance', views.InstanceViewSet, base_name='instance')
router.register(r'lawsuit', views.LawSuitViewSet, base_name='lawsuit')
router.register(
    r'court_division', views.CourtDivisionViewSet, base_name='court_division')
router.register(
    r'type_movement', views.TypeMovementViewSet, base_name='type_movement')
router.register(r'movement', views.MovementViewSet, base_name='movement')
router.register(r'organ', views.OrganViewSet, base_name='organ')
router.register(
    r'company/lawsuit',
    views.CompanyLawsuitViewSet,
    base_name='company-lawsuit')

urlpatterns = [
    # urls para tela de criacao de OS
    url(r'lawsuit_common',
        views.LawsuitApiView.as_view(),
        name='lawsuit_common'),
    url(r'movement_common',
        views.MovementApiView.as_view(),
        name='movement_common'),
    url(r'task_common', views.TaskApiView.as_view(), name='task_common'),
]
