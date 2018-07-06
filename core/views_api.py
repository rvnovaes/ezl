from rest_framework import mixins, viewsets, pagination
from core.models import Person
from core.serializers import PersonSerializer


class PersonViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
