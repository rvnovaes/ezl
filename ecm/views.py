import os
import os.path
import shutil
import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from . import utils
from .forms import UploadFileForm
from .models import Attachment

logger = logging.getLogger('django')


##
# Utils
##
def make_response(status=200, content_type='text/plain', content=None):
    """ Construct a response to an upload request.
    Success is indicated by a status of 200 and { "success": true }
    contained in the content.
    Also, content-type is text/plain by default since IE9 and below chokes
    on application/json. For CORS environments and IE9 and below, the
    content-type needs to be text/html.
    """
    response = HttpResponse()
    response.status_code = status
    response['Content-Type'] = content_type
    response.content = content
    return response


##
# Views
##
class UploadView(View):
    """ View which will handle all upload requests sent by Fine Uploader.
    See: https://docs.djangoproject.com/en/dev/topics/security/#user-uploaded-content-security
    Handles POST and DELETE requests.
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """A POST request. Validate the form and then handle the upload
        based ont the POSTed data. Does not handle extra parameters yet.
        """
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = request.POST

            attachment = Attachment(
                model_name=data.get('model_name'),
                object_id=data.get('object_id'),
                file=request.FILES.get('qqfile'),
                create_user_id=request.user.id
            )
            attachment.save()
            return make_response(content=json.dumps({'success': True}))
        else:
            return make_response(status=400,
                                 content=json.dumps({
                                     'success': False,
                                     'error': '%s' % repr(form.errors)
                                 }))


def ajax_get_attachments(request):
    attachments = Attachment.objects.filter(
        model_name=request.GET.get('model_name'),
        object_id=request.GET.get('object_id')
    )
    ret = []
    for attachment in attachments:
        ret.append({
            'file': attachment.file.name,
            'filename': attachment.filename,
            'id': attachment.id
        })

    return JsonResponse(ret, safe=False)

def ajax_dsrop_attachment(request):
    Attachment.objects.get(
        pk=request.GET.get('attachment_pk'),
    ).delete()
    return JsonResponse({'success': True})