from django import forms
from .models import Template
from .schemas import PARAMETERS
from django_admin_json_editor.admin import JSONEditorWidget


class CustomJSONEditorWidget(JSONEditorWidget):

    @property
    def media(self):
        css = {
            'all': [
                'django_admin_json_editor/bootstrap/css/bootstrap.min.css',
                'django_admin_json_editor/fontawesome/css/font-awesome.min.css',
                'django_admin_json_editor/style.css',
            ]
        }
        js = [
            'django_admin_json_editor/jquery/jquery.min.js',
            'django_admin_json_editor/bootstrap/js/bootstrap.min.js',
            'manager/jsoneditor.min.js',
        ]
        if self._sceditor:
            css['all'].append('django_admin_json_editor/sceditor/themes/default.min.css')
            js.append('django_admin_json_editor/sceditor/jquery.sceditor.bbcode.min.js')
        return forms.Media(css=css, js=js)


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        fields = '__all__'
        widgets = {
            'parameters': CustomJSONEditorWidget(PARAMETERS, collapsed=False, sceditor=True),
        }
