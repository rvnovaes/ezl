#!/usr/bin/python
# -*- encoding: utf-8 -*-
from django import template

register = template.Library()


@register.simple_tag
def field_type(field):
    """
    Get the name of the field class.
    """
    if hasattr(field, 'field'):
        field = field.field
    s = str(type(field.widget).__name__)
    s = s.rpartition('Input')[0]
    s = s.lower()
    return s