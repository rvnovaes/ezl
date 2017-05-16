from django import forms
from django.forms import ModelForm
from .models import TypeMovement


# Cria uma Form referência e adiciona o mesmo style a todos os widgets
class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control input-sm'


DISPLAY_CHOICES = (
    ("locationbox", "Display Location"),
    ("displaybox", "Display Direction")
)


class TypeMovementForm(ModelForm):
    class Meta:
        model = TypeMovement
        fields = ['name', 'legacy_code', 'uses_wo']

    name = forms.CharField(
        label=u"",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"required": "true", "placeholder": "Descrição"}),
        error_messages= {'required':'O campo de descrição é obrigatório','invalid': 'Enter a valid value'}
    )

    legacy_code = forms.CharField(
        label=u"",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Código Legado"}),
        error_messages={'required': 'O campo de código legado é obrigatório','invalid': 'Enter a valid value'}
    )

    uses_wo = forms.BooleanField(
        label="Utiliza ordem de serviço?",
        initial=False,
        required=True,
        error_messages={'required':''}
        )