from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import FieldDoesNotExist
from django.forms import ModelForm, TextInput
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from localflavor.br.forms import BRCPFField, BRCNPJField

from core.fields import CustomBooleanField
from core.models import ContactUs, Person, Address, Country, City, State, ContactMechanism, AddressType
from lawsuit.forms import BaseForm


class ContactForm(ModelForm, forms.Form):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone_number', 'message', 'is_active']

    name = forms.CharField(
        label=u"Nome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    email = forms.CharField(
        label=u"E-mail",
        required=True,
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control input-sm'})
    )

    phone_number = forms.CharField(
        label=u"Telefone",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    message = forms.CharField(
        label=u"Mensagem",
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control input-sm'})
    )


class ContactMechanismForm(ModelForm, forms.Form):
    class Meta:
        model = ContactMechanism
        fields = ['contact_mechanism_type', 'name', 'description', 'notes', 'is_active']

    # contact_mechanism_type = forms.Select()

    name = forms.CharField(
        label=u"Nome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    description = forms.CharField(
        label=u"Descrição",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    notes = forms.CharField(
        label=u"Observação",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control input-sm'})
    )


class PersonForm(BaseForm, forms.Form):
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name is 'cpf' and self.instance.legal_type == 'F':
                field.initial = self.instance.cpf_cnpj
            elif field_name is 'cnpj' and self.instance.legal_type == 'J':
                field.initial = self.instance.cpf_cnpj

    class Meta:
        model = Person
        fields = ['legal_name', 'name', 'legal_type', 'cpf', 'cnpj', 'is_lawyer', "is_correspondent", 'is_court',
                  'is_customer', 'is_supplier', 'is_active']

    legal_name = forms.CharField(
        required=True,
        max_length=255,
    )

    name = forms.CharField(
        required=False,
        max_length=255,
    )

    is_lawyer = CustomBooleanField(
        required=False,
    )

    is_correspondent = CustomBooleanField(
        required=False,
    )

    is_customer = CustomBooleanField(
        required=False,
    )

    is_supplier = CustomBooleanField(
        required=False,
    )

    is_court = CustomBooleanField(
        required=False
    )

    legal_type = forms.ChoiceField(
        required=True,
        widget=forms.Select(),
        choices=([('F', u'Física'),
                  ('J', u'Jurídica')])
    )

    cpf = BRCPFField(label="CPF", required=False, max_length=14, min_length=11, empty_value=None)
    cnpj = BRCNPJField(label="CNPJ", required=False, min_length=14, max_length=18)


class AddressForm(ModelForm, forms.Form):
    class Meta:
        model = Address
        fields = ['address_type', 'street', 'number', 'complement', 'city_region', 'zip_code', 'country',
                  'state', 'city', 'notes', 'is_active']

    address_type = forms.ModelChoiceField(
        label=u"Tipo de Endereço",
        queryset=AddressType.objects.filter(id__gte=1),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    street = forms.CharField(
        label=u"Logradouro",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    number = forms.CharField(
        label=u"Número",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    complement = forms.CharField(
        label=u"Complemento",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    city_region = forms.CharField(
        label=u"Bairro",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    zip_code = forms.CharField(
        label=u"CEP",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    country = forms.ModelChoiceField(
        label=u"País",
        queryset=Country.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # todo: alterar o id de acordo com o país
    state = forms.ModelChoiceField(
        label=u"Estado",
        # queryset=State.objects.none(),
        # queryset=State.objects.filter(country_id=-1).order_by('name'),
        queryset=State.objects.filter(id__gt=1).order_by('name'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})

    )

    is_active = CustomBooleanField(
        required=False,
        widget=(forms.HiddenInput())
    )

    # todo: alterar o id de acordo com o estato
    city = forms.ModelChoiceField(
        label=u"Município",
        # queryset=City.objects.none(),
        # queryset=City.objects.filter(state_id=-1).order_by('name'),
        queryset=City.objects.filter(id__gt=1).order_by('name'),
        required=True,
        widget=forms.Select(attrs={
            'onchange': "",
            'class': 'form-control'
        },
        )
    )

    notes = forms.CharField(
        label=u"Observação",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'})
    )


AddressFormSet = inlineformset_factory(Person, Address, form=AddressForm, extra=3)


class UserCreateForm(BaseForm, UserCreationForm):
    first_name = forms.CharField(
        label="Nome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label="Sobrenome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.CharField(
        label="E-mail",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label="Nome de usuário (login)",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label=_("Senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Confirmação de Senha"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    groups = forms.ModelMultipleChoiceField(label="Perfis", required=False, queryset=Group.objects.all().order_by('name'),
                                            widget=forms.SelectMultiple(attrs={'class': 'form-control profile-selector'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','email', 'password1', 'password2',
                   'groups', 'is_active']


class UserUpdateForm(UserChangeForm):
    first_name = forms.CharField(
        label="Nome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label="Sobrenome",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.CharField(
        label="E-mail",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label="Nome de usuário (login)",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    groups = forms.ModelMultipleChoiceField(label="Perfis", required=False, queryset=Group.objects.all().order_by('name'),
                                            widget=forms.SelectMultiple(attrs={'class': 'form-control profile-selector'}))

    is_active = CustomBooleanField(
        required=False,label="Ativo"
    )

    password = forms.CharField(
        label="Senha",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control','type':'password'})
    )


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','email', 'password',
                   'groups', 'is_active']

