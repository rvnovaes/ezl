from rest_framework import mixins, viewsets, pagination
from core.models import Person
from core.serializers import PersonSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope, TokenHasReadWriteScope
from rest_framework.decorators import permission_classes


class ApplicationView(object):
    def __init__(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()
        self.request = request
        print(self.request)


@permission_classes((TokenHasReadWriteScope,))
class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer

    def get_queryset(self):
        return Person.objects.filter(offices=self.request.auth.application.office)
