from django import forms
from django.forms.widgets import boolean_check, Input, DateTimeBaseInput
from django.utils import six
from django.utils import timezone
from django.utils.encoding import force_text
from django_filters import RangeFilter


class MDDateTimepicker(DateTimeBaseInput):
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'core/widgets/md_datetimepicker.html'

    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        # timezone_local = pytz.timezone(settings.TIME_ZONE)
        # utc = pytz.utc
        # time_local = utc.localize(self.min_date).astimezone(timezone_local)
        # d1 = pytz.timezone(settings.TIME_ZONE).localize(self.min_date)
        # d3 = timezone.localtime(self.min_date)
        context['widget']['min_date'] = timezone.localtime(self.min_date).strftime('%d/%m/%Y %H:%M')
        return context

    def __init__(self, attrs=None, format=None, min_date=None):
        super(MDDateTimepicker, self).__init__(attrs)
        self.format = format if format else None
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

    def __init__(self, attrs=None):
        widgets = (MDDateTimepicker(), MDDateTimepicker())
        super(MDRangeWidget, self).__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        # Method was removed in Django 1.11.
        return ' à '.join(rendered_widgets)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class DateTimeRangeField(forms.MultiValueField):
    widget = MDRangeWidget

    def __init__(self, fields=None, label=None, *args, **kwargs):
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

    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        super(MDDateTimeRangeFilter, self).__init__(*args, **kwargs)
