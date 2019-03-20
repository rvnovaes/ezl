from django import forms
from .models import Template
from .schemas import PARAMETERS
from django_admin_json_editor.admin import JSONEditorWidget


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        fields = '__all__'
        widgets = {
            'parameters': JSONEditorWidget(PARAMETERS, collapsed=False, sceditor=True),
        }
