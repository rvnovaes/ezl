import os
from rest_framework import routers
import core.views_api as core_views


router = routers.SimpleRouter()
router.register(r'persons', core_views.PersonViewSet)
urlpatterns = router.urls