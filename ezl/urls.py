import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from core.views import ClientAutocomplete
from ezl import settings
from task.views import DashboardView, TaskDetailView, DashboardSearchView

urlpatterns = [
                  url(r'^', include('core.urls')),
                  url(r'^admin/', admin.site.urls),
                  url(r'^processos/', include('lawsuit.urls'), name='lawsuit'),
                  url(r'^providencias/', include('task.urls'), name='task'),
                  url(r'^accounts/', include('allauth.urls')),
                  url(r'^dashboard/$', login_required(DashboardView.as_view()), name='dashboard'),
                  url(r'^dashboard/(?P<pk>[0-9]+)/$', login_required(TaskDetailView.as_view()), name='task_detail'),

                  url(r'^dashboard/filtrar/$', login_required(DashboardSearchView.as_view()), name='task_search'),
                  url(r'^client_form',
                      login_required(ClientAutocomplete.as_view()),
                      name='client_autocomplete'),

              ] + static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, "static/")) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
