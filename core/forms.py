from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.forms import ModelForm
from django.forms import CheckboxInput, formset_factory
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.urls.base import reverse

from dal import autocomplete
from localflavor.br.forms import BRCPFField, BRCNPJField
from material import Layout, Row

from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_username, user_pk_to_url_str, user_email
from allauth.utils import build_absolute_uri

from core.fields import CustomBooleanField
from core.models import ContactUs, Person, Address, City, ContactMechanism, AddressType, LegalType, Office, Invite
from core.utils import filter_valid_choice_form, get_office_field
from core.widgets import MDModelSelect2
from lawsuit.forms import BaseForm
from core.widgets import TypeaHeadForeignKeyWidget


class BaseModelForm(forms.ModelForm):

    def get_model_verbose_name(self):
        return self._meta.model._meta.verbose_name


class ContactForm(ModelForm):

    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone_number', 'message', 'is_active']

    name = forms.CharField(
        label=u'Nome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    email = forms.CharField(
        label=u'E-mail',
        required=True,
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control input-sm'})
    )

    phone_number = forms.CharField(
        label=u'Telefone',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    message = forms.CharField(
        label=u'Mensagem',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control input-sm'})
    )


class ContactMechanismForm(ModelForm):
    class Meta:
        model = ContactMechanism
        fields = ['contact_mechanism_type', 'name', 'description', 'notes', 'is_active']

    # contact_mechanism_type = forms.Select()

    name = forms.CharField(
        label=u'Nome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    description = forms.CharField(
        label=u'Descrição',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control input-sm'})
    )

    notes = forms.CharField(
        label=u'Observação',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control input-sm'})
    )


class AddressForm(BaseModelForm):
    city = forms.ModelChoiceField(
            queryset=filter_valid_choice_form(City.objects.filter(is_active=True)).order_by('name'),
            required=True,
            label='Cidade',
            widget=MDModelSelect2(url='city_autocomplete',
                                            attrs={
                                                'data-container-css': 'id_city_container',
                                                'class': 'select-with-search material-ignore',
                                                'data-minimum-input-length': 3,
                                                'data-placeholder': '',
                                                'data-label': 'Cidade',
                                                'data-autocomplete-light-language': 'pt-BR',}
                                            ))
    address_type = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(AddressType.objects.all().order_by('name')),
        empty_label='',
        required=True,
        label='Tipo',
        )

    is_active = CustomBooleanField(
        required=True,
        label='Ativo',
        widget=CheckboxInput(attrs={'class': 'filled-in',})
    )

    layout = Layout(
        Row('address_type'),
        Row('street', 'number', 'complement'),
        Row('city_region', 'city', 'zip_code'),
        Row('notes'),
        Row('is_active'),
    )

    class Meta:
        model = Address
        fields = [
            'city',
            'address_type', 'street', 'number', 'complement',
            'zip_code',
            'city_region',
            'notes',
            'is_active',
        ]

    def save(self, commit=True):
        saved = super().save(commit=False)
        saved.country = saved.city.state.country
        saved.state = saved.city.state
        if commit:
            saved.save()
        return saved


class PersonForm(BaseModelForm):
    legal_type = forms.ChoiceField(
            label='Tipo',
            choices=((x.value, x.format(x.value)) for x in LegalType),
            required=True,
        )

    auth_user = forms.ModelChoiceField(
        queryset=filter_valid_choice_form(User.objects.all().order_by('username')),
        empty_label='',
        required=False,
        label='Usuário do sistema',
        )

    class Meta:
        model = Person
        fields = ['legal_name', 'name', 'legal_type', 'cpf_cnpj',
                  'is_lawyer', 'is_customer', 'is_supplier', 'is_active', 'import_from_legacy', 'auth_user']

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('legal_type')
        document = cleaned_data.get('cpf_cnpj')
        if document_type == 'F' and document:
            try:
                BRCPFField().clean(document)
            except forms.ValidationError as exc:
                self._errors['cpf_cnpj'] = \
                    self.error_class(exc.messages)
                del cleaned_data['cpf_cnpj']
        elif document_type == 'J' and document:
            try:
                BRCNPJField().clean(document)
            except forms.ValidationError as exc:
                self._errors['cpf_cnpj'] = \
                    self.error_class(exc.messages)
                del cleaned_data['cpf_cnpj']

        return cleaned_data

    def __init__(self, *args, **kwargs):
        is_superuser = kwargs.pop('is_superuser', None)
        super().__init__(*args, **kwargs)
        if is_superuser:
            self.layout = Layout(
                Row('legal_name', 'name'),
                Row('legal_type', 'cpf_cnpj'),
                Row('auth_user', 'import_from_legacy'),
                Row('is_lawyer', 'is_customer', 'is_supplier', 'is_active'),
                )
        else:
            self.layout = Layout(
                Row('legal_name', 'name'),
                Row('legal_type', 'cpf_cnpj'),
                Row('is_lawyer', 'is_customer', 'is_supplier', 'is_active'))


AddressFormSet = inlineformset_factory(Person, Address, form=AddressForm, extra=1, max_num=1)


class UserCreateForm(BaseForm, UserCreationForm):
    first_name = forms.CharField(
        label='Nome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''})
    )

    last_name = forms.CharField(
        label='Sobrenome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.CharField(
        label='E-mail',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label='Nome de usuário (login)',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label=_('Senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Confirmação de Senha'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    groups = forms.ModelMultipleChoiceField(label='Perfis', required=True,
                                            queryset=Group.objects.all().order_by('name'),
                                            widget=forms.SelectMultiple(
                                                attrs={'class': 'form-control profile-selector'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2',
                  'groups', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request, profile=kwargs['instance'])


class UserUpdateForm(UserChangeForm):
    first_name = forms.CharField(
        label='Nome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label='Sobrenome',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.CharField(
        label='E-mail',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label='Nome de usuário (login)',
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    groups = forms.ModelMultipleChoiceField(label='Perfis', required=True,
                                            queryset=Group.objects.all().order_by('name'),
                                            widget=forms.SelectMultiple(
                                                attrs={'class': 'form-control profile-selector'}))

    is_active = CustomBooleanField(
        required=False,
        label='Ativo'
    )

    password = forms.CharField(
        label='Senha',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password',
                  'groups', 'is_active']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['office'] = get_office_field(self.request, profile=kwargs['instance'])


class ResetPasswordFormMixin(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        required=True,
        widget=forms.TextInput(attrs={
            "size": "30",
            "placeholder": _("Username"),
        })
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        self.users = filter_users_by_username(username)
        if not self.users:
            raise forms.ValidationError(_(u"O Usuário informado não está vinculado"
                                          " a nenhuma conta"))
        if not self.users[0].email or self.users[0].email == ' ':
            raise forms.ValidationError(_(u"O Usuário informado não possui e-mail registrado"))

        self.email = self.users[0].email
        return self.cleaned_data["username"]

    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        username = self.cleaned_data["username"]

        token_generator = kwargs.get("token_generator",
                                     default_token_generator)

        self.context = {}
        for user in self.users:

            temp_key = token_generator.make_token(user)

            # send the password reset email
            path = reverse("account_reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            url = build_absolute_uri(
                request, path)

            context = {"current_site": current_site,
                       "user": user,
                       "password_reset_url": url,
                       "request": request,
                       'username': username}

            email = user_email(user)
            get_adapter(request).send_mail(
                'account/email/password_reset_key',
                email,
                context)
            self.context = context
        return self.context

from core.widgets import TypeaHeadWidget


class OfficeForm(BaseModelForm):

    class Meta:
        model = Office
        fields = ['legal_name', 'name', 'legal_type', 'cpf_cnpj', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('legal_type')
        document = cleaned_data.get('cpf_cnpj')
        if document_type == 'F' and document:
            try:
                BRCPFField().clean(document)
            except forms.ValidationError as exc:
                self._errors['cpf_cnpj'] = \
                    self.error_class(exc.messages)
                del cleaned_data['cpf_cnpj']
        elif document_type == 'J' and document:
            try:
                BRCNPJField().clean(document)
            except forms.ValidationError as exc:
                self._errors['cpf_cnpj'] = \
                    self.error_class(exc.messages)
                del cleaned_data['cpf_cnpj']
        return cleaned_data


class AddressOfficeForm(AddressForm):
    class Meta:
        model = Address
        fields = ['zip_code', 'city_region', 'address_type', 'state', 'city', 'street', 'number',
                  'notes', 'is_active']


AddressOfficeFormSet = inlineformset_factory(Office, Address, form=AddressOfficeForm, extra=1,
                                             max_num=1)


class InviteForm(forms.ModelForm):
    person = forms.CharField(widget=TypeaHeadForeignKeyWidget(model=Person,
                                                              field_related='legal_name', name='person'))

    class Meta:
        model = Invite
        fields = ['office', 'person']
        exclude = ['is_active']


InviteOfficeFormSet = inlineformset_factory(Office, Invite, form=InviteForm, extra=1, max_num=1)
