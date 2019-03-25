import ast
from django.apps import apps
from .models import TemplateValue


def get_model_by_str(model_str):
    app_label, model_name = model_str.split('.')
    model = apps.get_model(app_label=app_label, model_name=model_name)
    return model


def get_filter_params_by_str(params_str):
    return ast.literal_eval(params_str)


def get_new_template_value_obj(template, office):
    value = {
        'office_id': office.id,
        'template_key': template.template_key,
        'template_type': template.type,
        'value': None,
    }
    return TemplateValue(office=office,
                         template=template,
                         create_user=template.create_user,
                         value=value)
