import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.views import ClientAutocomplete, GenericAutocompleteForeignKey, LoginCustomView, PasswordResetViewMixin, \
    CorrespondentAutocomplete, RequesterAutocomplete, ServiceAutocomplete, EditableListSave
from django.conf import settings
from task.views import DashboardView, TaskDetailView, DashboardSearchView, DashboardStatusCheckView

urlpatterns = [

    url(r'^the-cool-upload-method/', include('django_file_form.urls')),

    url(r'^', include('core.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', LoginCustomView.as_view(), name='account_login'),
    url(r'^accounts/password/reset/$', PasswordResetViewMixin.as_view(), name='account_reset_password'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^financeiro/', include('financial.urls'), name='financial'),
    url(r'^pesquisa/', include('survey.urls'), name='survey'),
    url(r'^processos/', include('lawsuit.urls'), name='lawsuit'),
    url(r'^providencias/', include('task.urls'), name='task'),
    url(r'^dashboard/$', login_required(DashboardView.as_view()), name='dashboard'),
    url(r'^chat/', include('chat.urls'), name='chat'), 
    url(r'^ecm/', include('ecm.urls', namespace='ecm')),

    url(r'^dashboard/(?P<pk>[0-9]+)/$',
        login_required(TaskDetailView.as_view()),
        name='task_detail'),

    url(r'^dashboard/filtrar/$',
        login_required(DashboardSearchView.as_view()),
        name='task_search'),

    url(r'^dashboard/verificar_status/$',
        login_required(DashboardStatusCheckView.as_view()),
        name='task_status_check'),


    url(r'^client_form',
        login_required(ClientAutocomplete.as_view()),
        name='client_autocomplete'),

    url(r'^correspondent_form',
        login_required(CorrespondentAutocomplete.as_view()),
        name='correspondent_autocomplete'),

    url(r'^requester_form',
        login_required(RequesterAutocomplete.as_view()),
        name='requester_autocomplete'),

    url(r'^service_form',
        login_required(ServiceAutocomplete.as_view()),
        name='service_autocomplete'),

    url(r'^generic_autocomplete_foreignkey',
        login_required(GenericAutocompleteForeignKey.as_view()),
        name='generic_autocomplete'),

    url(r'^qa/$', TemplateView.as_view(template_name='questionnaire/generic_survey.html')),

    url(r'^editable-list/save',
        csrf_exempt(EditableListSave.as_view()),
        name='editable-list-save'),

] + \
    static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static/')) + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
