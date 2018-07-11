from rest_framework import mixins, viewsets, pagination
from core.models import Person
from core.serializers import PersonSerializer

from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers


class PersonViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
