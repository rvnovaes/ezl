import os
from rest_framework import routers
import lawsuit.views_api as lawsuit_views
import core.views_api as core_views


router = routers.SimpleRouter()
router.register(r'persons', core_views.PersonViewSet)
router.register(r'court_district', lawsuit_views.CourtDistrictViewSet)
urlpatterns = router.urls