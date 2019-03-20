from django.shortcuts import render
from core.views import CustomLoginRequiredView, SingleTableViewMixin
from .models import TemplateAnswers
from .tables import TemplateAnswersTable


class TemplateAnswersListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = TemplateAnswers
    table_class = TemplateAnswersTable
