from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.forms import ModelForm

from core.fields import CustomBooleanField
from core.models import Person, State
from core.widgets import MDModelSelect2, MDDatePicker
from .models import TypeMovement, Instance, Movement, Folder, CourtDistrict, LawSuit, CourtDivision

#TODO Verificar se será utilizado datepicker
# from django.contrib.admin.widgets import AdminDateWidget
from core.utils import filter_valid_choice_form

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
        fields = ['name', 'is_active']

    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de descrição é obrigatório'}
    )


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
        fields = ['type_movement', 'person_lawyer', 'is_active']

    person_lawyer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_lawyer=True).order_by('name'),
        empty_label=u"Selecione...",
    )

    type_movement = forms.ModelChoiceField(
        queryset=TypeMovement.objects.filter(is_active=True).order_by('name'),
        empty_label=u"Selecione...",
    )


class FolderForm(BaseForm):

    class Meta:
        model = Folder
        fields = ['folder_number', 'person_customer', 'is_active']

    folder_number = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_customer=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='client_autocomplete', attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.order_fields(['folder_number', 'person_customer', 'is_active'])

        if not self.instance.pk:
            # Since the pk is set this is not a new instance            
            self.fields.pop('folder_number')
                      
        
class LawSuitForm(BaseForm):
    class Meta:
        model = LawSuit
        fields = ['law_suit_number', 'court_district', 'instance', 'person_court', 'court_division', 'person_lawyer',
                  'is_current_instance', 'is_active']

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=filter_valid_choice_form(
            Person.objects.filter(is_active=True, is_lawyer=True)).only('legal_name').order_by('name'), required=True
    )
    instance = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(Instance.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione", required=True
    )
    court_district = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(CourtDistrict.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione", required=True
    )
    person_court = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(filter_valid_choice_form(
            Person.objects.filter(is_active=True, is_court=True))).order_by('name'),
        empty_label=u"Selecione", required=True)
    court_division = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(CourtDivision.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione", required=True
    )
    law_suit_number = forms.CharField(max_length=255, required=True)
    is_current_instance = CustomBooleanField(initial=False, required=False)


class CourtDivisionForm(BaseForm):
    class Meta:
        model = CourtDivision
        fields = ['name', 'is_active']

        # legacy_code = forms.CharField(max_length=255, required=False)


class CourtDistrictForm(BaseForm):
    class Meta:
        model = CourtDistrict
        fields = ['name', 'state', 'is_active']

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.filter(is_active=True)),
        empty_label=u"Selecione"
    )
