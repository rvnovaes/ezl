# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from django import template

register = template.Library()


@register.simple_tag
def get_percent(val1, val2):
    try:
        percent = val1 * 100 / val2
    except ZeroDivisionError:
        percent = 0
    return percent
