import os
import os.path
import shutil
import json
import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from core.views import (AuditFormMixin, MultiDeleteViewMixin,
                        SingleTableViewMixin)
from core.messages import CREATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, \
    record_from_wrong_office
from core.utils import get_office_session
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from . import utils
from .forms import UploadFileForm, DefaultAttachmentRuleForm
from .tables import DefaulAttachmentRuleTable
from .models import Attachment, DefaultAttachmentRule

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


class DefaultAttachmentRuleListView(LoginRequiredMixin, SingleTableViewMixin):
    model = DefaultAttachmentRule
    table_class = DefaulAttachmentRuleTable
    ordering = ('correspondent', )
    paginate_by = 30


class DefaultAttachmentRuleCreateView(AuditFormMixin, CreateView):
    model = DefaultAttachmentRule
    form_class = DefaultAttachmentRuleForm
    success_url = reverse_lazy('defaultattachmentrule_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'defaultattachmentrule_list'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class DefaultAttachmentRuleUpdateView(AuditFormMixin, UpdateView):
    model = DefaultAttachmentRule
    form_class = DefaultAttachmentRuleForm
    success_url = reverse_lazy('defaultattachmentrule_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'defaultattachmentrule_list'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        office_session = get_office_session(request=request)
        if obj.office != office_session:
            messages.error(self.request, record_from_wrong_office(), )
            return HttpResponseRedirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)


class DefaultAttachmentRuleDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = DefaultAttachmentRule
    success_url = reverse_lazy('defaultattachmentrule_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'defaultattachmentrule_list'

