from django import forms
from django.forms import ModelForm
from django.forms.models import fields_for_model

# from django.contrib.admin.widgets import AdminDateWidget #TODO Verificar se será utilizado datepicker
from core.fields import CustomBooleanField
from core.models import Person, State
from .models import TypeMovement, Instance, LawSuit, Movement, Folder, CourtDistrict, LawSuitInstance


# Cria uma Form referência e adiciona o mesmo style a todos os widgets
class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.input_type != 'checkbox':
                field.widget.attrs['class'] = 'form-control'
            if field.widget.input_type == 'text':
                field.widget.attrs['style'] = 'width: 100%; display: table-cell; '

            # Preenche o o label de cada field do form de acordo com o verbose_name preenchido no modelo
            field.label = self._meta.model._meta.get_field(field_name).verbose_name


class TypeMovementForm(BaseForm):
    class Meta:
        model = TypeMovement
        fields = fields_for_model(TypeMovement,
                                  exclude={'active', 'create_user', 'alter_date', 'create_date', 'alter_user'})

    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de descrição é obrigatório'}
    )

    legacy_code = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de código legado é obrigatório'}
    )

    uses_wo = CustomBooleanField(
        initial=False,
        required=False,
    )


class InstanceForm(BaseForm):
    class Meta:
        model = Instance
        fields = ['name']

    name = forms.CharField(
        label=u"Nome da Instância",
        max_length=255,

    )

    # active = CustomBooleanField(  # forms.BooleanField(
    #     initial=True,
    #     required=False,
    # )


class MovementForm(BaseForm):
    class Meta:
        model = Movement
        fields = ['legacy_code', 'person_lawyer', 'type_movement', 'law_suit_instance', 'deadline']

    legacy_code = forms.CharField(
        label=u"Código Legado",
        max_length=255,
        required=True
    )

    person_lawyer = forms.ModelChoiceField(
        queryset=Person.objects.filter(active=True, is_lawyer=True),
        empty_label=u"Selecione...",
    )

    law_suit_instance = forms.ModelChoiceField(
        queryset=LawSuitInstance.objects.filter(active=True),
        empty_label=u"Selecione...",
    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(active=True),
        empty_label=u"Selecione...",
    )

    deadline = forms.DateTimeField(
        label=u"Data da Movimentação"
    )


class FolderForm(BaseForm):
    class Meta:
        model = Folder
        fields = fields_for_model(Folder,
                                  exclude={'active', 'create_user', 'alter_date', 'create_date', 'alter_user'})

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


class LawSuitForm(BaseForm):
    class Meta:
        model = LawSuit
        fields = fields_for_model(LawSuit,
                                  exclude={'active', 'create_user', 'alter_date', 'create_date', 'alter_user'})

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=Person.objects.filter(active=True, is_lawyer=True)
    )

    folder = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=Folder.objects.filter(active=True)
    )


class CourtDistrictForm(BaseForm):
    class Meta:
        model = CourtDistrict
        fields = fields_for_model(CourtDistrict,
                                  exclude=['active', 'create_user', 'alter_date', 'create_date', 'alter_user'])

    state = forms.ModelChoiceField(
        queryset=State.objects.filter(active=True),
        empty_label=u"Selecione"
    )


class LawSuitInstanceForm(BaseForm):
    class Meta:
        model = LawSuitInstance
        fields = fields_for_model(LawSuitInstance,
                                  exclude=['active', 'create_user', 'alter_date', 'create_date', 'alter_user'])

        law_suit_number = forms.CharField(max_length=255, required=True)

        law_suit = forms.ModelChoiceField(queryset=LawSuit.objects.filter(active=True),
                                          empty_label=u"Selecione")

        instance = forms.ModelChoiceField(queryset=Instance.objects.filter(active=True),
                                          empty_label=u"Selecione")

        court_district = forms.ModelChoiceField(queryset=CourtDistrict.objects.filter(active=True),
                                                empty_label=u"Selecione")

        person_court = forms.ModelChoiceField(queryset=Person.objects.filter(active=True),
                                              empty_label=u"Selecione")
        legacy_code = forms.CharField(
            max_length=255,
            required=True
        )
