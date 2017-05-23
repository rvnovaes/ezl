from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.forms.models import fields_for_model

# from django.contrib.admin.widgets import AdminDateWidget #TODO Verificar se será utilizado datepicker
from core.fields import CustomBooleanField
from core.models import Person, State
from .models import TypeMovement, Instance, LawSuit, Movement, Folder, Task, CourtDistrict


# Cria uma Form referência e adiciona o mesmo style a todos os widgets
class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.input_type != 'checkbox':
                field.widget.attrs['class'] = 'form-control'
            # Preenche o o label de cada field do form de acordo com o verbose_name preenchido no modelo
            field.label = self._meta.model._meta.get_field(field_name).verbose_name


class TypeMovementForm(BaseForm):
    class Meta:
        model = TypeMovement
        fields = ['name', 'legacy_code', 'uses_wo']

    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control checkbox'}),
        error_messages={'required': 'O campo de descrição é obrigatório'}
    )

    legacy_code = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de código legado é obrigatório'}
    )

    uses_wo = forms.BooleanField(
        initial=False,
        required=False,
    )


class InstanceForm(ModelForm):
    class Meta:
        model = Instance
        fields = ['name']

    name = forms.CharField(
        label=u"Nome da Instância",
        max_length=255,

    )


class MovementForm(ModelForm):
    class Meta:
        model = Movement
        fields = ['legacy_code', 'law_suit', 'person_lawyer', 'type_movement']

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
        required=True

    )

    law_suit = forms.ModelChoiceField(
        queryset=LawSuit.objects.filter(active=True),
        empty_label=u"Selecione...",
        label="Processo"
    )

    person_lawyer = forms.ModelChoiceField(
        queryset=Person.objects.filter(active=True, is_lawyer=True),
        empty_label=u"Selecione...",
        label=u"Advogado"
    )

    person_court = forms.ModelChoiceField(
        queryset=Person.objects.filter(active=True, is_court=True),
        empty_label=u"Selecione...",
        label=u"Tribunal"
    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(active=True),
        empty_label=u"Selecione...",
        label=u"Tipo de Movimentação"
    )

    deadline = forms.DateTimeField(
        label=u"Data da Movimentação"
    )


class FolderForm(BaseForm):
    class Meta:
        model = Folder
        fields = fields_for_model(Folder,
                                  exclude={'create_user', 'alter_date', 'create_date', 'alter_user'})

    # active = forms.BooleanField(
    #     label=u"ativo",
    #     initial=True,
    #     # widget=MDCheckboxInput()
    # )

    legacy_code = forms.CharField(
        max_length=255,
        required=True
    )

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(active=True),
        empty_label=u"Selecione...",
    )

    active = CustomBooleanField(  # forms.BooleanField(
        initial=True,
        required=False,
    )


LawSuitFormSet = inlineformset_factory(
    Folder, LawSuit,
    exclude={'create_user', 'alter_date', 'create_date', 'alter_user', 'active'},
    extra=1,
)


class LawSuitForm(ModelForm):
    class Meta:
        model = LawSuit
        fields = ['person_lawyer', 'folder']

    person_lawyer = forms.ModelChoiceField(
        label=u"Advogado",
        empty_label=u"Selecione",
        queryset=Person.objects.filter(active=True, is_lawyer=True)
    )

    folder = forms.ModelChoiceField(
        label=u"Pasta",
        empty_label=u"Selecione",
        queryset=Folder.objects.filter(active=True)
    )


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['legacy_code', 'movement', 'person', 'type_movement', 'delegation_date',
                  'acceptance_date', 'deadline_date', 'final_deadline_date', 'execution_deadline_date']

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
        required=True
    )

    movement = forms.ModelChoiceField(
        queryset=Movement.objects.filter(active=True),
        empty_label=u"Selecione...",
        label=u"Movimentação"
    )

    person = forms.ModelChoiceField(
        label=u"Correpondente",
        empty_label=u"Selecione...",
        queryset=Person.objects.filter(active=True, is_corresponding=True)

    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(active=True),
        empty_label=u"Selecione...",
        label=u"Tipo de Movimentação"
    )
    # TODO verificar como aplicar os formulários com dateTimeField
    delegation_date = forms.DateTimeField(
        label=u"Data de abertura"
    )

    acceptance_date = forms.DateTimeField(
        label=u"Data Fechamento"
    )

    deadline_date = forms.DateTimeField(
        label=u"Prazo"
    )

    final_deadline_date = forms.DateTimeField(
        label=u"Prazo Fatal"
    )

    execution_deadline_date = forms.DateTimeField(
        label=u"Prazo Execução Fatal"
    )


class CourtDistrictForm(BaseForm):
    class Meta:
        model = CourtDistrict
        fields = fields_for_model(CourtDistrict, exclude=['create_user', 'alter_date', 'create_date', 'alter_user'])

    state = forms.ModelChoiceField(
        queryset=State.objects.filter(active=True),
        empty_label=u"Selecione..."
    )
