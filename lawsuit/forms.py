from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.forms import ModelForm
from django.forms.models import fields_for_model

from core.fields import CustomBooleanField
from core.models import Person, State
from core.widgets import MDModelSelect2, MDDatePicker
from .models import TypeMovement, Instance, Movement, Folder, CourtDistrict, LawSuit, CourtDivision


# from django.contrib.admin.widgets import AdminDateWidget #TODO Verificar se será utilizado datepicker


# Cria uma Form referência e adiciona o mesmo style a todos os widgets
class BaseForm(ModelForm):
    is_active = CustomBooleanField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.title = self._meta.model._meta.verbose_name
        for field_name, field in self.fields.items():
            if field.widget.input_type != 'checkbox':
                field.widget.attrs['class'] = 'form-control'
            if field.widget.input_type == 'text':
                field.widget.attrs['style'] = 'width: 100%; display: table-cell; '

            # Preenche o o label de cada field do form de acordo com o verbose_name preenchido no modelo

            try:
                field.label = self._meta.model._meta.get_field(field_name).verbose_name
            except FieldDoesNotExist:
                pass


class TypeMovementForm(BaseForm):
    class Meta:
        model = TypeMovement
        fields = fields_for_model(TypeMovement,
                                  exclude={'create_user', 'alter_date', 'create_date', 'alter_user', 'system_prefix',
                                           'legacy_code', 'uses_wo'})

    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de descrição é obrigatório'}
    )

    # legacy_code = forms.CharField(
    #     max_length=255,
    #     required=False,
    #     error_messages={'required': 'O campo de código legado é obrigatório'}
    # )

    # uses_wo = CustomBooleanField(
    #     initial=False,
    #     required=False,
    # )


class InstanceForm(BaseForm):
    class Meta:
        model = Instance
        fields = ['name', 'is_active']

    name = forms.CharField(
        label=u"Nome da Instância",
        max_length=255,

    )


class MovementForm(BaseForm):
    class Meta:
        model = Movement
        fields = ['person_lawyer', 'type_movement', 'deadline', 'is_active']

    # legacy_code = forms.CharField(
    #     label=u"Código Legado",
    #     max_length=255,
    #     required=False
    # )

    person_lawyer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_lawyer=True),
        empty_label=u"Selecione...",
    )

    # law_suit = forms.ModelChoiceField(
    #     queryset=LawSuit.objects.filter(is_active=True),
    #     empty_label=u"Selecione...",
    # )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(is_active=True),
        empty_label=u"Selecione...",
    )

    deadline = forms.DateTimeField(
        label=u"Data da Movimentação",
        widget=MDDatePicker(attrs={'class': 'form-control'},
                            format='DD/MM/YYYY'
                            )
    )


class FolderForm(BaseForm):
    
    class Meta:
        model = Folder
        fields = fields_for_model(Folder,
                                  exclude={'create_user', 'alter_date', 'create_date', 'alter_user', 'system_prefix',
                                           'legacy_code'})

    #legacy_code = forms.CharField(
    #     max_length=255,
    #     required=False
    #)
    
    

    folder_number = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}),initial=Folder.increment())

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_customer=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='client_autocomplete', attrs={'class': 'form-control'})
    )
    
    
class LawSuitForm(BaseForm):
    class Meta:
        model = LawSuit
        fields = fields_for_model(LawSuit,
                                  exclude={'create_user', 'alter_date', 'create_date', 'alter_user', 'system_prefix',
                                           'legacy_code', 'folder'})

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=Person.objects.filter(is_active=True, is_lawyer=True).only('legal_name'), required=True
    )
    # folder = forms.ModelChoiceField(
    #     empty_label=u"Selecione",
    #     queryset=Folder.objects.filter(is_active=True), required=True
    # )
    instance = forms.ModelChoiceField(
        queryset=Instance.objects.filter(is_active=True),
        empty_label=u"Selecione", required=True
    )
    court_district = forms.ModelChoiceField(
        queryset=CourtDistrict.objects.filter(is_active=True),
        empty_label=u"Selecione", required=True
    )
    person_court = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_court=True),
        empty_label=u"Selecione", required=True)
    court_division = forms.ModelChoiceField(
        queryset=CourtDivision.objects.filter(is_active=True),
        empty_label=u"Selecione", required=True
    )
    law_suit_number = forms.CharField(max_length=255, required=True)
    is_current_instance = CustomBooleanField(initial=False, required=False)


class CourtDivisionForm(BaseForm):
    class Meta:
        model = CourtDivision
        fields = fields_for_model(CourtDivision,
                                  exclude=['create_user', 'alter_date', 'create_date', 'alter_user', 'system_prefix',
                                           'legacy_code'])

        # legacy_code = forms.CharField(max_length=255, required=False)


class CourtDistrictForm(BaseForm):
    class Meta:
        model = CourtDistrict
        fields = fields_for_model(CourtDistrict,
                                  exclude=['create_user', 'alter_date', 'create_date', 'alter_user', 'legacy_code',
                                           'system_prefix'])

    state = forms.ModelChoiceField(
        queryset=State.objects.filter(is_active=True),
        empty_label=u"Selecione"
    )
