from django import forms
from django.forms import ModelForm
from .models import TypeMovement


# Cria uma Form referência e adiciona o mesmo style a todos os widgets
class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control input-sm'


class TypeMovementForm(BaseForm,forms.Form):
    class Meta:
        model = TypeMovement
        fields = ['name','legacy_code','uses_wo']

    name = forms.CharField(
        label=u"Nome",
        max_length=255,
        required=True,
        widget=forms.TextInput()
    )

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
    )

    use_wo = forms.BooleanField(
        label=u"Utiliza Ordem de Serviço?",
        required=True,
        widget=forms.CheckboxInput
    )
