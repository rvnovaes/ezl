import json
from django.contrib.postgres.forms import JSONField
from django.db.models.fields import NOT_PROVIDED
from import_export.fields import Field
from task.messages import *
from task.utils import self_or_none


class JSONFieldMixin(JSONField):
    def prepare_value(self, value):
        data = json.loads(super().prepare_value(value))
        return json.dumps(data, indent=4, ensure_ascii=False)


class CustomFieldImportExport(Field):

    def __init__(self, column_name_dict, attribute=None, column_name=None, widget=None,
                 default=NOT_PROVIDED, readonly=False, saves_null_values=True):
        super().__init__(attribute, column_name, widget, default, readonly, saves_null_values)
        self.column_name_dict = column_name_dict

    def clean(self, data):
        """
        Translates the value stored in the imported datasource to an
        appropriate Python object and returns it.
        """
        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError(COLUMNS_NOT_AVAILABLE.format(self.column_name, list(data)))

        try:
            old_value = value
            value = self.widget.clean(value, row=data)
            if value in self.empty_values:
                column_property = self.column_name_dict.get(self.column_name)
                if column_property and column_property.get('required'):
                    raise ValueError(REQUIRED_COLUMN.format(self.column_name))
                if old_value not in self.empty_values and column_property:
                    data['warnings'].append([INCORRECT_NATURAL_KEY.format(column_property.get('verbose_name'),
                                                                          self.column_name,
                                                                          old_value)])
        except ValueError as e:
            column_name = self.column_name_dict.get(self.column_name, self.column_name)
            if not column_name == self.column_name:
                column_name = column_name.get('column_name')
            raise ValueError(COLUMN_ERROR.format(column_name, e))

        if value in self.empty_values and self.default != NOT_PROVIDED:
            if callable(self.default):
                return self.default()
            return self.default

        return self_or_none(value)
