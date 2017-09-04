import django_tables2 as tables
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django_tables2.utils import A, AttributeDict  # alias for Accessor

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
            'selection', 'name', 'is_lawyer', 'is_correspondent', 'is_court', 'legal_type',
            'cpf_cnpj', 'is_active', 'is_customer', 'is_supplier', 'auth_user', 'legacy_code')
        model = Person
        fields = ['selection', 'name', 'legal_type', 'cpf_cnpj', 'is_lawyer', 'is_correspondent', 'is_court',
                  'is_customer', 'is_supplier', 'auth_user', 'is_active', 'legacy_code']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pessoas cadastradas"
        row_attrs = {
            'data_href': lambda record: '/pessoas/' + str(record.pk) + '/'
        }


class UserTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)
    is_staff = tables.BooleanColumn()
    is_superuser = tables.BooleanColumn()


    class Meta:
        sequecence = (
            'selection', 'username', 'first_name', 'last_name', 'email',
            'last_login', 'date_joined', 'is_active', )
        model = User
        fields = ['selection', 'username', 'first_name', 'last_name', 'email', 'is_active'
                  'last_login', 'date_joined']
        attrs = {"class": "table-striped table-bordered"}

        empty_text = "Não existem usuários cadastradas"

        row_attrs = {
            'data_href': lambda record: '/usuarios/' + str(record.pk) + '/'
        }