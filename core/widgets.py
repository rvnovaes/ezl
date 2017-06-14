from django.forms.widgets import boolean_check, Input, DateTimeBaseInput
from django.utils import six
from django.utils.encoding import force_text


class MDDateTimepicker(DateTimeBaseInput):
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'core/widgets/md_datetimepicker.html'

    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['min_date'] = self.min_date.strftime('%d/%m/%Y %H:%M')
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
