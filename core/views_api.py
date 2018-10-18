from rest_framework import viewsets
from core.models import Person, Company
from core.serializers import PersonSerializer, CompanySerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from core.views import remove_invalid_registry


class OfficeMixinViewSet(viewsets.ModelViewSet):

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(office=self.request.auth.application.office, is_active=True)


class ApplicationView(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        print(self.request)


@api_view(['GET'])
@permission_classes((TokenHasReadWriteScope, ))
def user_session_view(request):
    data = {'user_id': request.user.pk, 'username': request.user.username}
    return Response(data)


@permission_classes((TokenHasReadWriteScope, ))
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    model = Person

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        return self.queryset.filter(offices=self.request.auth.application.office)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(users__user=self.request.user)
