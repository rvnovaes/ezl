from django import forms
from django.forms import ModelForm
from core.fields import CustomBooleanField
from core.models import Person, State, Address, Office
from financial.models import CostCenter
from core.widgets import MDModelSelect2
from .models import (TypeMovement, Instance, Movement, Folder, CourtDistrict,
                     LawSuit, CourtDivision, Organ)
from core.utils import filter_valid_choice_form, get_office_field, get_office_session
from dal import autocomplete
from localflavor.br.forms import BRCNPJField
from material import Layout, Row
from django.forms.models import inlineformset_factory
from core.widgets import TypeaHeadForeignKeyWidget
from core.forms import BaseForm, BaseModelForm


class TypeMovementForm(BaseForm):
    class Meta:
        model = TypeMovement
        fields = ['office', 'name', 'is_active']

    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de descrição é obrigatório'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class InstanceForm(BaseForm):
    class Meta:
        model = Instance
        fields = ['office', 'name', 'is_active']

    name = forms.CharField(
        label=u"Nome da Instância",
        max_length=255,

    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class MovementForm(BaseForm):
    class Meta:
        model = Movement
        fields = ['office', 'type_movement', 'is_active']

    type_movement = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeMovement.objects.filter(is_active=True)).order_by(
            'name'),
        empty_label=u"Selecione...",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class FolderForm(BaseForm):
    class Meta:
        model = Folder
        fields = ['office', 'folder_number', 'person_customer', 'cost_center', 'is_active']

    folder_number = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_customer=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='client_autocomplete',
                              forward=['office'],
                              attrs={'class': 'form-control'})
    )

    cost_center = forms.ModelChoiceField(
        queryset=CostCenter.objects.filter(is_active=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='costcenter_autocomplete', attrs={'class': 'form-control'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        self.order_fields(['office', 'folder_number', 'person_customer', 'is_active'])

        if not self.instance.pk:
            # Since the pk is set this is not a new instance
            self.fields.pop('folder_number')


class LawSuitForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(LawSuitForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)

        def get_option(o):
            return '{}/{}'.format(o.court_district.name, o.legal_name)

        choices = [(organ.pk, get_option(organ)) for organ in
                   Organ.objects.filter(office=get_office_session(self.request))]
        self.fields['organ'].choices = choices

    class Meta:
        model = LawSuit
        fields = ['office', 'law_suit_number', 'organ', 'instance', 'court_division',
                  'person_lawyer', 'opposing_party',
                  'is_current_instance', 'is_active', 'court_district']

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=filter_valid_choice_form(
            Person.objects.filter(is_active=True, is_lawyer=True)).only('legal_name').order_by(
            'name'), required=True
    )
    organ = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(Organ.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione",
        required=True,
        initial=None,
        widget=autocomplete.ListSelect2(url='organ_autocomplete',
                                        attrs={
                                            'class': 'select-with-search',
                                            'data-placeholder': 'Comarca/Tribunal'
                                        }))

    instance = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(Instance.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione", required=True
    )
    court_division = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(CourtDivision.objects.filter(is_active=True)).order_by(
            'name'),
        empty_label=u"Selecione", required=True
    )
    opposing_party = forms.CharField(required=False)
    law_suit_number = forms.CharField(max_length=255, required=True)
    is_current_instance = CustomBooleanField(initial=False, required=False)
    court_district = forms.CharField(required=False, widget=forms.HiddenInput(), initial=None)

    def clean(self):
        res = super(LawSuitForm, self).clean()
        res['court_district'] = None
        if res.get('organ'):
            res['court_district'] = res.get('organ').court_district
        elif self.data.get('organ'):
            res['organ'] = Organ.objects.filter(pk=self.data.get('organ')).first()
            if res['organ']:
                res['court_district'] = res['organ'].court_district
        return res

class CourtDivisionForm(BaseForm):
    class Meta:
        model = CourtDivision
        fields = ['office', 'name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class CourtDistrictForm(BaseForm):
    class Meta:
        model = CourtDistrict
        fields = ['name', 'state', 'is_active']

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.filter(is_active=True)),
        empty_label=u"Selecione"
    )


class OrganForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        for field_name, field in self.fields.items():
            if field_name is 'cnpj':
                field.initial = self.instance.cpf_cnpj

    cpf_cnpj = BRCNPJField(label="CNPJ", widget=forms.TextInput(
        attrs={'data-mask': '99.999.999/9999-99'}
    ))

    class Meta:
        model = Organ
        fields = ['office', 'legal_name', 'cpf_cnpj', 'court_district', 'is_active']
