from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views_api as views

router = routers.DefaultRouter()

router.register(r'court_district', views.CourtDistrictViewSet)


urlpatterns = [
	url(r'^api/v1', include(router.urls)),
    url(r'lawsuit$', login_required(views.LawsuitApiView.as_view()),
        name='lawsuit_api'),
    url(r'movement$', login_required(views.MovementApiView.as_view()),
        name='movement_api'),
    url(r'task$', login_required(views.TaskApiView.as_view()),
        name='task_api'),
]
