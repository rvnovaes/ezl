import json
from django.contrib.postgres.forms import JSONField


class JSONFieldMixin(JSONField):
    def prepare_value(self, value):
        data = json.loads(super().prepare_value(value))
        return json.dumps(data, indent=4)
