from django import forms
from .models import BillingDetails
from core.models import Address, AddressType
from core.forms import BaseModelForm, AddressForm


class CombinedFormBase(forms.Form):
    form_classes = []

    def __init__(self, *args, **kwargs):
        super(CombinedFormBase, self).__init__(*args, **kwargs)
        for f in self.form_classes:
            name = f.__name__.lower()
            setattr(self, name, f(*args, **kwargs))
            form = getattr(self, name)
            self.fields.update(form.fields)
            self.initial.update(form.initial)

    def is_valid(self):
        isValid = True
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            if not form.is_valid():
                isValid = False
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super(CombinedFormBase, self).is_valid():
            isValid = False
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            self.errors.update(form.errors)
        return isValid

    def clean(self):
        cleaned_data = super(CombinedFormBase, self).clean()
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            cleaned_data.update(form.cleaned_data)
        return cleaned_data


class BillingDetailsForm(BaseModelForm):
    PHONE_CHOICES= (
        ("RES", "Residencial"),
        ("COM", "Comercial"),
    )
    phone_type = forms.ChoiceField(choices=PHONE_CHOICES, label="Tipo de telefone")
    # # card_name = forms.CharField(
    # #     label=u'Nome completo')

    password = forms.CharField(label="Senha", required=False)

    class Meta:
        fields = ['card_name', 'email', 'cpf_cnpj', 'birth_date', 'phone_number']
        exclude = ['documents']
        model = BillingDetails
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'card_name': forms.TextInput(attrs={'style': 'text-transform:uppercase'}),
            'password': forms.PasswordInput(attrs={"type": "password"}),
        }


class BillingAddressCombinedForm(CombinedFormBase):
    form_classes = [BillingDetailsForm, AddressForm]
