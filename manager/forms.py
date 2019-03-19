from django import forms
from .models import Template
import json
from .schemas import PARAMETERS
from core.forms import code_mirror_schema
from django.forms import ModelForm, Form
from django_admin_json_editor.admin import JSONEditorWidget


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        fields = '__all__'
        widgets = {
            'parameters': JSONEditorWidget(PARAMETERS, collapsed=False),
        }
