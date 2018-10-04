from rest_framework.validators import UniqueValidator
from .models import Person
from .utils import get_office_api


class CpfCnpjOfficeUniqueValidator(UniqueValidator):
    def set_context(self, serializer_field):
        super().set_context(serializer_field)
        self.queryset = Person.objects.filter(
            offices=get_office_api(serializer_field.context['request']))

    def filter_queryset(self, value, queryset):
        return super().filter_queryset(value, queryset)
