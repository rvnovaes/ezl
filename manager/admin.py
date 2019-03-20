from django.contrib import admin
from manager.models import Template
from manager.forms import TemplateForm


@admin.register(Template)
class TemplateModelAdmin(admin.ModelAdmin):
    form = TemplateForm
    list_display = ('name', 'key_schema', 'type')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['create_user'].initial = request.user
        else:
            form.base_fields['alter_user'].initial = request.user
        return form
