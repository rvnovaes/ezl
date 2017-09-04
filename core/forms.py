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
        fields = ['legal_name', 'name', 'legal_type', 'cpf', 'cnpj', 'auth_user',
                  'is_lawyer', "is_correspondent", 'is_court', 'is_customer', 'is_supplier', 'is_active']

    legal_name = forms.CharField(
        required=False,
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

    auth_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Selecione..."

    )


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
        label="Email",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label="Usuário",
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

    groups = forms.ModelMultipleChoiceField(label="Perfis", required=False, queryset=Group.objects.all(),
                                            widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2',
                  'email', 'groups', 'is_active']


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
        label="Email",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label="Usuário",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    groups = forms.ModelMultipleChoiceField(label="Perfis", required=False, queryset=Group.objects.all(),
                                            widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    is_active = CustomBooleanField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.title = self._meta.model._meta.verbose_name
        for field_name, field in self.fields.items():
            if isinstance(field.widget, TextInput):
                if field.widget.input_type != 'checkbox':
                    field.widget.attrs['class'] = 'form-control'
                if field.widget.input_type == 'text':
                    field.widget.attrs['style'] = 'width: 100%; display: table-cell; '

            # Preenche o o label de cada field do form de acordo com o verbose_name preenchido no modelo

            try:
                field.label = self._meta.model._meta.get_field(field_name).verbose_name
            except FieldDoesNotExist:
                pass

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'is_active',
                  'email', 'groups']


        # # data for 'profiles' field
        # def __init__(self, *args, **kwargs):
        #     # Only in case we build the form from an instance
        #     # (otherwise, 'profiles' list should be empty)
        #     if kwargs.get('instance'):
        #         # We get the 'initial' keyword argument or initialize it
        #         # as a dict if it didn't exist.
        #         initial = kwargs.setdefault('initial', {})
        #         # The widget for a ModelMultipleChoiceField expects
        #         # a list of primary key for the selected data.
        #         initial['groups'] = [t.pk for t in kwargs['instance'].groups.all()]
        #
        #     forms.ModelForm.__init__(self, *args, **kwargs)

        # Overriding save allows us to process the value of 'profiles' field
        # def save(self, commit=True):
        #     # Get the unsave UserEZL instance
        #     instance = forms.ModelForm.save(self, False)
        #
        #     # Prepare a 'save_m2m' method for the form,
        #     old_save_m2m = self.save_m2m
        #
        #     def save_m2m():
        #         old_save_m2m()
        #         # This is where we actually link the UserEZL with profiles
        #         instance.groups.clear()
        #         for group in self.cleaned_data['groups']:
        #             instance.groups.add(group)
        #
        #     self.save_m2m = save_m2m
