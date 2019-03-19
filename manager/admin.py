from django.contrib import admin
from manager.models import Template
from manager.forms import TemplateForm


@admin.register(Template)
class TemplateModelAdmin(admin.ModelAdmin):
    form = TemplateForm
