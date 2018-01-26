# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_file_form.forms import FileFormMixin, MultipleUploadedFileField

from .models import Attachment, DefaultAttachmentRule
from core.forms import BaseModelForm
from core.utils import filter_valid_choice_form, get_office_field
from core.models import City, State, Person
from core.widgets import MDModelSelect2
from lawsuit.models import CourtDistrict
from task.models import TypeTask


class UploadFileForm(forms.Form):
    """ This form represents a basic request from Fine Uploader.
    The required fields will **always** be sent, the other fields are optional
    based on your setup.
    Edit this if you want to add custom parameters in the body of the POST
    request.
    """
    qqfile = forms.FileField()
    qquuid = forms.CharField()
    qqfilename = forms.CharField()
    qqpartindex = forms.IntegerField(required=False)
    qqchunksize = forms.IntegerField(required=False)
    qqpartbyteoffset = forms.IntegerField(required=False)
    qqtotalfilesize = forms.IntegerField(required=False)
    qqtotalparts = forms.IntegerField(required=False)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = '__all__'


class DefaultAttachmentRuleForm(BaseModelForm):

    name = forms.CharField(label="Nome",
                            required=True)

    description = forms.CharField(
        label=u'Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control input-sm',
                                     'rows': '2'})
    )

    type_task = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(TypeTask.objects.all()).order_by('name'),
        empty_label='',
        required=False,
        label='Tipo de Serviço',
    )

    person_customer = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_customer=True),
        widget=MDModelSelect2(
            url='client_autocomplete',
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Cliente'
            }),
        required=False,
        label="Cliente"
    )

    state = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(State.objects.all()).order_by('initials'),
        empty_label='',
        required=False,
        label='UF',
    )

    court_district = forms.ModelChoiceField(
        queryset=CourtDistrict.objects.filter(),
        widget=MDModelSelect2(
            url='courtdistrict_autocomplete',
            forward=['state'],
            attrs={
                'class': 'select-with-search material-ignore form-control',
                'data-placeholder': '',
                'data-label': 'Comarca'
            }),
        required=False,
        label="Comarca"
    )

    city = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(City.objects.filter(is_active=True)).order_by('name'),
        required=False,
        label='Cidade',
        widget=MDModelSelect2(url='city_autocomplete',
                              attrs={
                                  'data-container-css': 'id_city_container',
                                  'class': 'select-with-search material-ignore',
                                  'data-minimum-input-length': 3,
                                  'data-placeholder': '',
                                  'data-label': 'Cidade',
                                  'data-autocomplete-light-language': 'pt-BR', }
                              ))

    class Meta:
        model = DefaultAttachmentRule
        fields = ('name', 'description', 'type_task', 'person_customer', 'state', 'court_district', 'city', 'office')

    def clean(self):
        cleaned_data = super().clean()
        type_task = cleaned_data.get('type_task')
        person_customer = cleaned_data.get('person_customer')
        state = cleaned_data.get('state')
        court_district = cleaned_data.get('court_district')
        city = cleaned_data.get('city')

        if not type_task and not person_customer and not state and not court_district and not city:
            raise forms.ValidationError(_(u"Deve ser informado pelo menos um dos seguintes campos:"
                                          u" Tipo de Serviço,"+ chr(12) +
                                          u" Cliente,"
                                          u" UF,"
                                          u" Comarca"
                                          u" ou Cidade"))
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request)


class DefaultAttachmentRuleCreateForm(FileFormMixin, DefaultAttachmentRuleForm):
    documents = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta(DefaultAttachmentRuleForm.Meta):
        fields = DefaultAttachmentRuleForm.Meta.fields + ('documents',)