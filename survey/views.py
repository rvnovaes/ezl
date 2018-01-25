from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from core.messages import (CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE,
                           DELETE_SUCCESS_MESSAGE)
from core.views import (AuditFormMixin, MultiDeleteViewMixin,
                        SingleTableViewMixin)
from .forms import SurveyForm
from .models import Survey, SurveyPermissions
from .tables import SurveyTable


class SurveyListView(LoginRequiredMixin, PermissionRequiredMixin, SingleTableViewMixin):
    model = Survey
    table_class = SurveyTable
    ordering = ('id', )
    permission_required = (SurveyPermissions.can_edit_surveys, )


class SurveyCreateView(AuditFormMixin, CreateView):
    model = Survey
    form_class = SurveyForm
    success_url = reverse_lazy('survey_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'survey_list'
    permission_required = (SurveyPermissions.can_edit_surveys, )


class SurveyUpdateView(PermissionRequiredMixin, AuditFormMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    success_url = reverse_lazy('survey_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'survey_list'
    permission_required = (SurveyPermissions.can_edit_surveys, )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SurveyDeleteView(PermissionRequiredMixin, AuditFormMixin, MultiDeleteViewMixin):
    model = Survey
    success_url = reverse_lazy('survey_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'survey_list'
    permission_required = (SurveyPermissions.can_edit_surveys, )
