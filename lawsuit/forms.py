from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.forms import ModelForm
from core.fields import CustomBooleanField
from core.models import Person, State, Address
from core.widgets import MDModelSelect2
from .models import (TypeMovement, Instance, Movement, Folder, CourtDistrict,
                     LawSuit, CourtDivision, Organ, CostCenter)
from core.utils import filter_valid_choice_form
from dal import autocomplete
from localflavor.br.forms import BRCNPJField
from material import Layout, Row
from django.forms.models import inlineformset_factory


class BaseModelForm(forms.ModelForm):
    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


# TODO: Por ser uma implementacao base que esta sendo utilizada por outros apps, talvez compensa levar esta implementacao para o app core.
class BaseForm(ModelForm):
    """
    Cria uma Form referência e adiciona o mesmo style a todos os widgets
    """
    is_active = CustomBooleanField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.title = self._meta.model._meta.verbose_name
        for field_name, field in self.fields.items():
            try:
                if field.widget.input_type != 'checkbox':
                    field.widget.attrs['class'] = 'form-control'
                if field.widget.input_type == 'text':
                    field.widget.attrs['style'] = 'width: 100%; display: table-cell; '
                # Preenche o o label de cada field do form de acordo com o verbose_name preenchido no modelo
                try:
                    field.label = self._meta.model._meta.get_field(field_name).verbose_name
                except FieldDoesNotExist:
                    pass
            except AttributeError:
                pass


class CostCenterForm(BaseModelForm):

    layout = Layout(
        Row('name', 'is_active'),
    )

    legacy_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CostCenter
        fields = ['name', 'legacy_code', 'is_active']


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
        fields = ['type_movement', 'is_active']

    type_movement = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeMovement.objects.filter(is_active=True)).order_by(
            'name'),
        empty_label=u"Selecione...",
    )


class FolderForm(BaseForm):
    class Meta:
        model = Folder
        fields = ['folder_number', 'person_customer', 'cost_center', 'is_active']

    folder_number = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True, is_customer=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='client_autocomplete', attrs={'class': 'form-control'})
    )

    cost_center = forms.ModelChoiceField(
        queryset=CostCenter.objects.filter(is_active=True),
        empty_label=u"Selecione...",
        widget=MDModelSelect2(url='costcenter_autocomplete', attrs={'class': 'form-control'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        self.order_fields(['folder_number', 'person_customer', 'is_active'])

        if not self.instance.pk:
            # Since the pk is set this is not a new instance
            self.fields.pop('folder_number')


class LawSuitForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(LawSuitForm, self).__init__(*args, **kwargs)

        def get_option(o):
            return '{}/{}'.format(o.court_district.name, o.legal_name)
        choices = [(organ.pk, get_option(organ)) for organ in Organ.objects.all()]
        self.fields['organ'].choices = choices

    class Meta:
        model = LawSuit
        fields = ['law_suit_number', 'organ', 'instance', 'court_division',
                  'person_lawyer',
                  'is_current_instance', 'is_active', 'court_district']

    person_lawyer = forms.ModelChoiceField(
        empty_label=u"Selecione",
        queryset=filter_valid_choice_form(
            Person.objects.filter(is_active=True, is_lawyer=True)).only('legal_name').order_by(
            'name'), required=True
    )
    organ = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(
            filter_valid_choice_form(Organ.objects.filter(is_active=True))).order_by('name'),
        empty_label=u"Selecione", required=True, initial=None,
        widget=autocomplete.ListSelect2(url='organ_autocomplete', forward=['person_lawyer'], attrs={
            'class': 'select-with-search', 'data-placeholder': 'Comarca/Tribunal'}))

    instance = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(Instance.objects.filter(is_active=True)).order_by('name'),
        empty_label=u"Selecione", required=True
    )
    court_division = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(CourtDivision.objects.filter(is_active=True)).order_by(
            'name'),
        empty_label=u"Selecione", required=True
    )
    law_suit_number = forms.CharField(max_length=255, required=True)
    is_current_instance = CustomBooleanField(initial=False, required=False)
    court_district = forms.CharField(required=False, widget=forms.HiddenInput(), initial=None)

    def clean(self):
        res = super(LawSuitForm, self).clean()
        res['court_district'] = None
        if res.get('organ'):
            res['court_district'] = res.get('organ').court_district
        return res


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


class OrganForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name is 'cnpj':
                field.initial = self.instance.cpf_cnpj
    layout = Layout(
        Row('legal_name', 'cpf_cnpj'),
        Row('court_district', 'is_active')
    )

    class Meta:
        model = Organ
        fields = ['legal_name', 'cpf_cnpj', 'court_district', 'is_active']

    def clean(self):
        cleaned_data = super(OrganForm, self).clean()
        document = cleaned_data.get('cpf_cnpj')
        if document:
            try:
                BRCNPJField().clean(document)
            except forms.ValidationError as exc:
                self._errors['cpf_cnpj'] = \
                    self.error_class(exc.messages)
                del cleaned_data['cpf_cnpj']
        return cleaned_data
