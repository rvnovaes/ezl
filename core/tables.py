import django_tables2 as tables
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
            '<div class="checkbox"><label><input %s name="selection" onclick="toggle(this)"/></label></div>'
            % attrs.as_html())

    def render(self, value, bound_column, record):
        default = {
            'type': 'checkbox',
            'name': bound_column.name,
            'value': value
        }
        if self.is_checked(value, record):
            default.update({
                'checked': 'checked',
            })

        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        return mark_safe('<div class="checkbox"><label><input name="selection"'
                         ' type="checkbox" value="{{ record.pk }}" />'
                         '</label></div>')


class PersonTable(tables.Table):
    selection = CheckBoxMaterial(accessor="pk", orderable=False)

    name = tables.LinkColumn(viewname='person_update', attrs={'a': {'target': '_blank'}}, args=[A('pk')])

    class Meta:
        sequecence = (
            'selection', 'name', 'is_lawyer', 'is_correspondent', 'is_court', 'legal_type', 'auth_user',
            'cpf_cnpj')
        model = Person
        fields = ['selection', 'name', 'is_lawyer', 'is_correspondent', 'is_court', 'legal_type', 'auth_user',
                  'cpf_cnpj']
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "Não existem pessoas cadastradas"
