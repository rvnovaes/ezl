import django_tables2 as tables
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django_tables2.utils import AttributeDict  # alias for Accessor

from .models import Person


class CheckBoxMaterial(tables.CheckBoxColumn):
    def __init__(self, attrs=None, checked=None, **extra):
        self.checked = checked
        kwargs = {'orderable': False, 'attrs': attrs}
        kwargs.update(extra)
        super(CheckBoxMaterial, self).__init__(**kwargs)

    # @property
    # def selectable(self):
    #     return True;

    def header(self):
        default = {'type': 'checkbox'}
        general = self.attrs.get('input')
        specific = self.attrs.get('th__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs['selectable'] = True
        return mark_safe(
            '<div class="checkbox"><label><input %s id="selection_header"  onclick="toggle(this)"/></label></div>'
            % attrs.as_html())

    def render(self, value, bound_column, record):
        default = {
            'type': 'checkbox',
            'name': bound_column.name,
            'value': value,
        }
        if self.is_checked(value, record):
            default.update({
                'checked': 'checked',
            })

        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs['id'] = record.id
        return mark_safe('<div class="checkbox"><label><input name="selection"'
                         ' type="checkbox" %s onclick="showDeleteButton(this)"/>'
                         '</label></div>' % attrs.as_html())


class PersonTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    class Meta:
        sequecence = (
            'selection', 'legal_name', 'name', 'is_lawyer', 'is_correspondent', 'is_court', 'legal_type',
            'cpf_cnpj', 'is_active', 'is_customer', 'is_supplier', 'auth_user', 'legacy_code')
        model = Person
        fields = ['selection', 'legal_name', 'name', 'legal_type', 'cpf_cnpj', 'is_lawyer', 'is_correspondent',
                  'is_court', 'is_customer', 'is_supplier', 'auth_user', 'is_active', 'legacy_code']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pessoas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/pessoas/' + str(record.pk) + '/'
        }


class UserTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    is_staff = tables.BooleanColumn()
    is_superuser = tables.BooleanColumn()

    def __init__(self, *args, first_name='Nome', last_name='Sobrenome', is_active="Ativo",
                 username="Nome de usuário (login)", email="e-mail", last_login="Último acesso",
                 date_joined="Data de registro"
                 ,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns['first_name'].verbose_name = first_name
        self.base_columns['last_name'].verbose_name = last_name
        self.base_columns['username'].verbose_name = username
        self.base_columns['email'].verbose_name = email
        self.base_columns['is_active'].verbose_name = is_active
        self.base_columns['last_login'].verbose_name = last_login
        self.base_columns['date_joined'].verbose_name = date_joined
        self.exclude = ('is_staff','is_superuser')
    class Meta:

        model = User
        fields = ['selection', 'first_name', 'last_name', 'username', 'email',
                  'last_login', 'date_joined', 'is_active']
        attrs = {"class": "table-striped table-bordered"}

        empty_text = "Não existem usuários cadastradas"

        row_attrs = {
            'data_href': lambda record: '/usuarios/' + str(record.pk) + '/'
        }
