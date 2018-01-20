from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter
def get_item_data_ini(dictionary, key):
    return dictionary.get(key + '_ini', '')


@register.filter
def get_item_data_fim(dictionary, key):
    return dictionary.get(key + '_fim', '')


@register.filter
def get_check_box_format(dictionary, key):
    if dictionary.get(key) == 'on':
        return 'checked'
    return ''


@register.filter
def get_is_active_selected(dictionary, value):
    if dictionary.get('is_active') == value:
        return 'selected'
    return ''

@register.filter
def get_choice_format_value(choice):
    return choice[0]


@register.filter
def get_choice_format_text(choice):
    return choice[1]


@register.filter
def get_choice_choice_selected(value, choice):
    return 'selected' if value == choice[0] else ''


@register.filter
def get_class_field(type_field):
    map_class_fields = {
        'text': 'col-sm-4',
        'date': 'col-sm-2',
        'checkbox': 'col-sm-1',
        'number': 'col-sm-1'
    }
    return map_class_fields.get(type_field, 'col-sm-1')


@register.filter
def get_fields_order(fields):
    return fields.sort()


@register.filter
def append_ast_if_req (field):
    if field.field.required:
        return field.label + '*'
    else:
        return field.label


@register.filter
def label_capitalizer(text):
    return str(text).capitalize()


@register.filter
def get_class_name(value):
    return value.__class__.__name__
