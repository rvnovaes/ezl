# -*- coding:utf-8 -*-

from enum import Enum


# tipo do campo
class FieldType(Enum):
    INTEGER = 'integer'
    STRING = 'string'
    DECIMAL = 'decimal'
    DATE = 'date'
    DATETIME = 'datetime'

# def format_field():
#     if