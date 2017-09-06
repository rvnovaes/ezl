from dal.widgets import QuerySetSelectMixin
from django import forms
from django.forms.widgets import boolean_check, Input, DateTimeBaseInput, ChoiceWidget
from django.utils import six, translation
from django.utils import timezone
from django.utils.encoding import force_text
from django_filters import RangeFilter

from ezl import settings


class MDDateTimepicker(DateTimeBaseInput):
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'core/widgets/md_datetimepicker.html'

    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['min_date'] = timezone.localtime(self.min_date).strftime('%d/%m/%Y %H:%M')
        context['widget']['format'] = self.format
        return context

    def __init__(self, attrs=None, format=None, min_date=None):
        super(MDDateTimepicker, self).__init__(attrs)
        self.format = format if format else 'DD/MM/YYYY'
        self.min_date = min_date if min_date else None


class MDDatePicker(DateTimeBaseInput):
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'core/widgets/md_datepicker.html'

    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['format'] = self.format
        if self.min_date:
            context['widget']['min_date'] = timezone.localtime(self.min_date).strftime('%d/%m/%Y')

        if value and not (value is ''):
            context['widget']['value'] = value.strftime('%d/%m/%Y')
            # self.value = value.strftime('%d/%m/%Y %H:%M')
        return context

    def __init__(self, attrs=None, format=None, min_date=None):
        super(MDDatePicker, self).__init__(attrs)
        self.format = format if format else 'DD/MM/YYYY'
        self.min_date = min_date if min_date else None


class MDCheckboxInput(Input):
    input_type = 'checkbox'
    template_name = 'core/widgets/md_checkbox.html'

    def __init__(self, attrs=None, check_test=None):
        super(MDCheckboxInput, self).__init__(attrs)
        # check_test is a callable that takes a value and returns True
        # if the checkbox should be checked for that value.
        self.check_test = boolean_check if check_test is None else check_test

    def format_value(self, value):
        """Only return the 'value' attribute if value isn't empty."""
        if value is True or value is False or value is None or value == '':
            return
        return force_text(value)

    def get_context(self, name, value, attrs):
        if self.check_test(value):
            if attrs is None:
                attrs = {}
            attrs['checked'] = True

        return super(MDCheckboxInput, self).get_context(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            # A missing value means False because HTML form submission does not
            # send results for unselected checkboxes.
            return False
        value = data.get(name)
        # Translate true and false strings to boolean values.
        values = {'true': True, 'false': False}
        if isinstance(value, six.string_types):
            value = values.get(value.lower(), value)
        return bool(value)

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False


class MDRangeWidget(forms.MultiWidget):
    template_name = 'core/widgets/md_range_datetimepicker.html'
    format = "DD/MM/YYYY"

    def __init__(self, format=None, attrs=None):
        self.format = format if format else "DD/MM/YYYY"
        widgets = (MDDateTimepicker(), MDDateTimepicker())
        super(MDRangeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]

    def get_context(self, name, value, attrs):
        context = super(MDRangeWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            widget_name = '%s_%s' % (name, i)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = '%s_%s' % (id_, i)
            else:
                widget_attrs = final_attrs
            subwidgets.append(widget.get_context(widget_name, widget_value, widget_attrs)['widget'])
        context['widget']['subwidgets'] = subwidgets
        context['widget']['format'] = self.format
        return context


class DateTimeRangeField(forms.MultiValueField):
    widget = MDRangeWidget

    def __init__(self, fields=None, format=None, label=None, *args, **kwargs):

        if fields is None:
            fields = (
                forms.DateTimeField(widget=MDDateTimepicker(attrs={'class': 'form-control'})),
                forms.DateTimeField(widget=MDDateTimepicker(attrs={'class': 'form-control'})))
            super(DateTimeRangeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return slice(*data_list)
        return None


class MDDateTimeRangeFilter(RangeFilter):
    field_class = DateTimeRangeField
    format = None

    def __init__(self, name=None, label=None, format=None, *args, **kwargs):
        self.name = name
        self.format = format if format else 'DD/MM/YYYY'
        # self.field.widget = MDRangeWidget(format=self.format)
        kwargs['format'] = self.format
        super(MDDateTimeRangeFilter, self).__init__(*args, **kwargs)


class MDSelect2WidgetMixin(object):
    """Mixin for Select2 widgets."""

    def build_attrs(self, *args, **kwargs):
        attrs = super(MDSelect2WidgetMixin, self).build_attrs(*args, **kwargs)
        lang_code = self._get_language_code()
        if lang_code:
            attrs.setdefault('data-autocomplete-light-language', lang_code)
        # search min length
        attrs.setdefault('data-minimum-input-length', 3)
        return attrs

    def _get_language_code(self):
        lang_code = translation.get_language()
        if lang_code:
            lang_code = translation.to_locale(lang_code).replace('_', '-')
        return lang_code

    def _media(self):
        """Automatically include static files for the admin."""
        _min = '' if settings.DEBUG else 'min.'
        i18n_file = ()
        lang_code = self._get_language_code()

        if lang_code:
            i18n_file = (
                'autocomplete_light/vendor/select2/dist/js/i18n/{}.js'.format(
                    lang_code),
            )
        css = (
            'autocomplete_light/vendor/select2/dist/css/select2.{}css'.format(
                _min),
            'autocomplete_light/select2.css',
        )
        js = ('autocomplete_light/jquery.init.js',
              'autocomplete_light/autocomplete.init.js',
              'autocomplete_light/vendor/select2/dist/js/select2.full.{}js'.format(
                  _min),
              ) + i18n_file + (
                 'libs/django-autocomplete-light-3.2.9/select2.js',
             )

        return forms.Media(css={'all': css}, js=js)

    media = property(_media)
    autocomplete_function = 'select2'


class MDSelect(ChoiceWidget):
    input_type = 'select'
    template_name = 'core/widgets/md_select.html'
    option_template_name = 'core/widgets/md_select_option.html'
    add_id_index = False
    checked_attribute = {'selected': True}
    option_inherits_attrs = False

    def get_context(self, name, value, attrs):
        context = super(MDSelect, self).get_context(name, value, attrs)
        if self.allow_multiple_selected:
            context['widget']['attrs']['multiple'] = 'multiple'
        return context

    @staticmethod
    def _choice_has_empty_value(choice):
        """Return True if the choice's value is empty string or None."""
        value, _ = choice
        return (
            (isinstance(value, six.string_types) and not bool(value)) or
            value is None
        )

    def use_required_attribute(self, initial):
        """
        Don't render 'required' if the first <option> has a value, as that's
        invalid HTML.
        """
        use_required_attribute = super(MDSelect, self).use_required_attribute(initial)
        # 'required' is always okay for <select multiple>.
        if self.allow_multiple_selected:
            return use_required_attribute

        first_choice = next(iter(self.choices), None)
        return use_required_attribute and first_choice is not None and self._choice_has_empty_value(first_choice)


class MDModelSelect2(QuerySetSelectMixin,
                     MDSelect2WidgetMixin,
                     MDSelect):
    """Select widget for QuerySet choices and Select2."""
