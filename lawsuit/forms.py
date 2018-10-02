from django import forms
from django.forms import ModelForm
from core.fields import CustomBooleanField
from core.models import Person, State, Address, Office
from financial.models import CostCenter
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
        fields = ['office', 'name', 'is_default', 'is_active']

    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={'required': 'O campo de descrição é obrigatório'})

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
        queryset=filter_valid_choice_form(
            TypeMovement.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione...",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class FolderForm(BaseForm):
    class Meta:
        model = Folder
        fields = [
            'office', 'folder_number', 'person_customer', 'cost_center',
            'is_default', 'is_active'
        ]

    folder_number = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    person_customer = forms.CharField(
        label="Cliente",
        required=True,
        widget=TypeaHeadForeignKeyWidget(
            model=Person,
            field_related='legal_name',
            name='person_customer',
            url='/client_form'))
    cost_center = forms.CharField(
        required=False,
        label="Centro de Custos",
        widget=TypeaHeadForeignKeyWidget(
            model=CostCenter,
            field_related='name',
            name='cost_center',
            url='/financeiro/centros-de-custos/autocomplete'))

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        self.order_fields(
            ['office', 'folder_number', 'person_customer', 'is_active'])

        if not self.instance.pk:
            # Since the pk is set this is not a new instance
            self.fields.pop('folder_number')


class LawSuitForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(LawSuitForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)

        def get_option(o):
            return '{}/{}'.format(o.court_district.name, o.legal_name)

        choices = [(organ.pk, get_option(organ))
                   for organ in Organ.objects.filter(
                       office=get_office_session(self.request))]
        self.fields['organ'].choices = choices

    class Meta:
        model = LawSuit
        fields = [
            'office', 'law_suit_number', 'court_district', 'organ', 'instance',
            'court_division', 'person_lawyer', 'opposing_party',
            'is_current_instance', 'is_active'
        ]

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=filter_valid_choice_form(
            Person.objects.filter(
                is_active=True,
                is_lawyer=True)).only('legal_name').order_by('name'),
        required=False)
    court_district = forms.CharField(
        label='Comarca',
        required=True,
        widget=TypeaHeadForeignKeyWidget(
            model=CourtDistrict,
            field_related='name',
            name='court_district',
            url='/processos/courtdistrict_autocomplete'))

    organ = forms.CharField(
        label='Órgão',
        required=False,
        widget=TypeaHeadForeignKeyWidget(
            model=Organ,
            field_related='legal_name',
            name='organ',
            url='/processos/organ_autocomplete'))

    instance = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(
            Instance.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione",
        required=True)
    court_division = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(
            CourtDivision.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione",
        required=False)
    opposing_party = forms.CharField(required=False)
    law_suit_number = forms.CharField(max_length=255, required=True)
    is_current_instance = CustomBooleanField(initial=False, required=False)


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
        queryset=filter_valid_choice_form(
            State.objects.filter(is_active=True)),
        empty_label=u"Selecione")


class OrganForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(OrganForm, self).__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)
        for field_name, field in self.fields.items():
            if field_name is 'cnpj':
                field.initial = self.instance.cpf_cnpj

    cpf_cnpj = BRCNPJField(
        label="CNPJ",
        widget=forms.TextInput(attrs={'data-mask': '99.999.999/9999-99'}),
        required=False,
    )

    court_district = forms.CharField(
        label="Comarca",
        widget=TypeaHeadForeignKeyWidget(
            model=CourtDistrict,
            field_related='name',
            name='court_district',
            url='/processos/typeahead/search/comarca'))

    class Meta:
        model = Organ
        fields = [
            'office', 'legal_name', 'cpf_cnpj', 'court_district', 'is_active'
        ]
