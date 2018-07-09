import os
from django.conf.urls import url, include
from core.urls_api import router as router_core
from lawsuit.urls_api import router as router_lawsuit
from rest_framework.documentation import include_docs_urls


urlpatterns = [
	url(r'^', include((router_lawsuit.urls, 'lawsuit'), namespace='lawsuit')),
    url(r'^', include((router_core.urls, 'core'), namespace='core')),
]