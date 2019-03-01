from rest_framework import viewsets
from core.models import Person, Company, Office
from core.serializers import PersonSerializer, CompanySerializer, OfficeSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from core.views import remove_invalid_registry
from django.contrib.auth.models import Group



class OfficeMixinViewSet(viewsets.ModelViewSet):

    @remove_invalid_registry
    def get_queryset(self, *args, **kwargs):
        invalid_registry = kwargs.get('remove_invalid', None)
        if invalid_registry:
            self.queryset = self.queryset.exclude(id=invalid_registry)
        if self.request.auth.application.office:
            return self.queryset.filter(office=self.request.auth.application.office, is_active=True)    
        return super().get_queryset()        


class ApplicationView(object):
    def __init__(self, request, *args, **kwargs):
        self.request = request


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


class CorrespondentViewSet(PersonViewSet):
    def get_queryset(self, *args, **kwargs):
        correspondents = Person.objects.filter(
            auth_user__groups__in=Group.objects.filter(
                name__icontains='correspondent')).order_by().distinct()
        q = self.request.query_params.get('q', None)
        if q:
            correspondents = correspondents.filter(legal_name__unaccent__icontains=q)
        return correspondents


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(users__user=self.request.user)


class OfficeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OfficeSerializer

    def get_queryset(self):
        q = self.request.query_params.get('q', None)
        if q:
            return Office.objects.filter(legal_name__icontains=q)
        return Office.objects.all()

