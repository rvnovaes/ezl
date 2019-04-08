from decimal import Decimal
from .enums import TypeTemplate
from .models import TemplateValue
from .utils import get_filter_params_by_str, get_model_by_str


class GenericTemplateValues(object):
    # Classe responsavel por buscar o valor de um template de configuracao
    def __init__(self,
                 office,
                 template_key=tuple(),
                 only_active=True):
        self.office = office
        self.template_key = template_key
        self.only_active = only_active
        self.convert_class = {
            TypeTemplate.BOOLEAN.name: BooleanConvertTemplateValue(),
            TypeTemplate.INTEGER.name: IntegerConvertTemplateValue(),
            TypeTemplate.DECIMAL.name: DecimalConvertTemplateValue(),
            TypeTemplate.FOREIGN_KEY.name: FKConvertTemplateValue(),
        }
        self.search_criteria_dict = {
            'office': 'office',
            'active': 'is_active',
            'template_key': 'value__template_key__in',
        }

    @property
    def _search_criteria(self):
        search_criteria = {self.search_criteria_dict['office']: self.office}
        if self.only_active:
            search_criteria[self.search_criteria_dict['active']] = True
        if self.template_key:
            search_criteria[self.search_criteria_dict['template_key']] = self.template_key
        return search_criteria

    @property
    def instance_values(self):
        search_criteria = self._search_criteria

        return TemplateValue.objects.filter(
            **search_criteria).select_related('template')

    def _get_python_value(self, value_obj):
        return self.convert_class.get(
            value_obj.template.type, GenericConvertTemplateValue()
        ).to_python(value_obj.value, value_obj.template.parameters)

    def _get_default_value(self, template_obj):
        return self.convert_class.get(
            template_obj.type, GenericConvertTemplateValue()
        ).default_value(template_obj.parameters)

    def dispatch(self):
        values = self.instance_values
        values_list = [
            self._get_python_value(value)
            for value in values
        ]

        return values_list


class ListTemplateValues(GenericTemplateValues):

    @property
    def list_template_values(self):
        return self.dispatch()

    def get_value_by_key(self, key):
        template_value = GetTemplateValue(self.office, key)
        return template_value.value


class GetTemplateValue(GenericTemplateValues):

    def __init__(self,
                 office,
                 template_key,
                 only_active=True):
        super().__init__(office, template_key, only_active)
        self.search_criteria_dict['template_key'] = 'value__template_key'

    @property
    def template_values(self):
        return self.dispatch()

    @property
    def get_template_value_obj(self):
        return self.instance_values.first()

    @property
    def value(self):
        values = self.dispatch()
        return values.get('value')

    @value.setter
    def value(self, value):
        template_value = self.instance_values.first()
        template_value.value['value'] = value
        template_value.save()

    @property
    def default_value(self):
        template_obj = self.get_template_value_obj.template
        return self._get_default_value(template_obj)

    def dispatch(self):
        values = super().dispatch()
        if values:
            return values[0]
        return {}


class GenericConvertTemplateValue(object):

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def _get_value_from_dict(value_dict, default_value=''):
        return value_dict.get('value', default_value)

    @staticmethod
    def _set_dict_value(value_dict, value):
        value_dict['value'] = value

    def to_python(self, value_dict, extra_params):
        value = self._get_value_from_dict(value_dict)
        self._set_dict_value(value_dict, str(value))
        return value_dict

    def default_value(self, template_parameters):
        return ''


class BooleanConvertTemplateValue(GenericConvertTemplateValue):

    def to_python(self, value_dict, extra_params):
        value = self._get_value_from_dict(value_dict)
        self._set_dict_value(value_dict, True if value == 'on' else False)
        return value_dict

    def default_value(self, template_parameters):
        default_value = template_parameters.get('boolean_default', 'on')
        return 'on' if default_value == 'True' else ''


class IntegerConvertTemplateValue(GenericConvertTemplateValue):

    def to_python(self, value_dict, extra_params):
        value = self._get_value_from_dict(value_dict, '0')
        self._set_dict_value(value_dict, int(value))
        return value_dict


class DecimalConvertTemplateValue(GenericConvertTemplateValue):

    def to_python(self, value_dict, extra_params):
        value = self._get_value_from_dict(value_dict, '0') or '0'
        self._set_dict_value(value_dict, Decimal(value))
        return value_dict


class FKConvertTemplateValue(GenericConvertTemplateValue):

    def to_python(self, value_dict, extra_params):
        value = None
        try:
            value_id = int(self._get_value_from_dict(value_dict, '0'))
            fk_parameters = extra_params.get('foreign_key_default', [{}])[0]
            model = get_model_by_str(fk_parameters.get('model'))
            filter_params = get_filter_params_by_str(fk_parameters.get('extra_params', '{}'))
            filter_params['id'] = value_id
            value = model.objects.filter(**filter_params).first()
        except Exception:
            pass
        finally:
            self._set_dict_value(value_dict, value)
        return value_dict
