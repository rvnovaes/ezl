import os
from django.conf.urls import url, include
from core.urls_api import router as router_core
from lawsuit.urls_api import router as router_lawsuit
from financial.urls_api import router as router_financial
from task.urls_api import router as router_task
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken import views


urlpatterns = [	
	url(r'^', include((router_lawsuit.urls, 'lawsuit'), namespace='lawsuit')),
    url(r'^', include((router_core.urls, 'core'), namespace='core')),
    url(r'^', include((router_financial.urls, 'financial'), namespace='financial')),
    url(r'^', include((router_task.urls, 'task'), namespace='task')),       
]