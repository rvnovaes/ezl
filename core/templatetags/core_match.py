# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django import template
from django.apps import apps

register = template.Library()


@register.simple_tag
def get_percent(val1, val2):
    try:
        percent = val1 * 100 / val2
    except ZeroDivisionError:
        percent = 0
    return percent


@register.simple_tag
def get_model_instance(app, model, pk):
    try:
        model = apps.get_model(app_label=app, model_name=model)
        return model.objects.filter(pk=pk).first()
    except:
        return None
