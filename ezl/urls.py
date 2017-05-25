import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from ezl import settings

urlpatterns = [
                  url(r'^', include('core.urls')),
                  url(r'^admin/', admin.site.urls),
                  url(r'^processos/', include('lawsuit.urls'), name='lawsuit'),
                  url(r'^accounts/', include('allauth.urls')),
              ] + static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
