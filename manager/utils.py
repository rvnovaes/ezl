import ast
from django.apps import apps


def get_model_by_str(model_str):
    app_label, model_name = model_str.split('.')
    model = apps.get_model(app_label=app_label, model_name=model_name)
    return model


def get_filter_params_by_str(params_str):
    return ast.literal_eval(params_str)


def get_template_by_key(key):
    from .models import Template

    return Template.objects.filter(template_key=key).first()


def new_template_value_obj(template, office, value=None):
    from .models import TemplateValue

    value_dict = {
        'office_id': office.id,
        'template_key': template.template_key,
        'template_type': template.type,
        'value': value,
    }
    return TemplateValue(office=office,
                         template=template,
                         create_user=template.create_user,
                         value=value_dict)


def create_template_value(template, office, value=None):
    template_value = new_template_value_obj(template, office, value)
    return template_value.save()


def update_template_value(template_value, new_value):
    value = template_value.value
    value['value'] = new_value
    value['office_id'] = template_value.office_id
    value['template_type'] = template_value.template.type
    value['template_key'] = template_value.template.template_key
    template_value.value = value
    template_value.save()


def get_template_value_values(office, template_key):
    from .template_values import GetTemplateValue
    manager = GetTemplateValue(office, template_key)
    return manager.template_values


def get_template_value_value(office, template_key):
    from .template_values import GetTemplateValue
    manager = GetTemplateValue(office, template_key)
    return manager.value