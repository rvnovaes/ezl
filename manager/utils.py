import ast
from django.apps import apps


def get_model_by_str(model_str):
    app_label, model_name = model_str.split('.')
    model = apps.get_model(app_label=app_label, model_name=model_name)
    return model


def get_filter_params_by_str(params_str):
    return ast.literal_eval(params_str)
