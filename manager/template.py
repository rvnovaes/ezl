from .enums import TypeTemplate
from .template_values import BooleanConvertTemplateValue, IntegerConvertTemplateValue, DecimalConvertTemplateValue, \
    FKConvertTemplateValue, GenericConvertTemplateValue


class GenericTemplate(object):
    def __init__(self,
                 template):
        self.template = template
        self.template_key = template.template_key
        self.template_type = template.type
        self.convert_class = {
            TypeTemplate.BOOLEAN.name: BooleanConvertTemplateValue(),
            TypeTemplate.INTEGER.name: IntegerConvertTemplateValue(),
            TypeTemplate.DECIMAL.name: DecimalConvertTemplateValue(),
            TypeTemplate.FOREIGN_KEY.name: FKConvertTemplateValue(),
        }

    @property
    def default_value(self):
        return self.convert_class.get(
            self.template_type, GenericConvertTemplateValue()
        ).default_value(self.template.parameters)

    @property
    def default_python_value(self):
        value_dict = {'value': self.default_value}
        value_dict = self.convert_class.get(
            self.template_type, GenericConvertTemplateValue()
        ).to_python(value_dict, self.template.parameters)
        return value_dict.get('value', '')
