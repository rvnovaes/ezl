# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django import template
from django.apps import apps

register = template.Library()


@register.simple_tag
def get_percent(val1, val2):
    try:
        if not val1:
            val1 = 0
        if not val2:
            val2 = 0
        percent = int(val1) * 100 / int(val2)
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


@register.simple_tag
def get_opened_office_invites(office):
    return office.invites_offices.filter(status='N').all()


@register.simple_tag
def get_opened_person_invites(office):
    return office.invites.filter(status='N', invite_from='P').all()
