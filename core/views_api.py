from rest_framework import mixins, viewsets, pagination
from core.models import Person, Company
from core.serializers import PersonSerializer, CompanySerializer
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers
from rest_framework.decorators import permission_classes, api_view



class ApplicationView(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        print(self.request)

@api_view(['GET'])
@permission_classes((TokenHasReadWriteScope,))
def user_session_view(request):
	data = {'user_id': request.user.pk, 'username': request.user.username}
	return Response(data)


@permission_classes((TokenHasReadWriteScope,))
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def get_queryset(self):
        return Person.objects.filter(offices=self.request.auth.application.office)



class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = CompanySerializer

	def get_queryset(self):
		return Company.objects.filter(users__user=self.request.user)
