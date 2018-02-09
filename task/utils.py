from ecm.models import DefaultAttachmentRule, Attachment
from task.models import *
from core.utils import get_office_session
from django.db.models import Q


def get_task_attachment(self, form):
    attachmentrules = DefaultAttachmentRule.objects.filter(
        Q(office=get_office_session(self.request)),
        Q(Q(type_task=form.instance.type_task) | Q(type_task=None)),
        Q(Q(person_customer=form.instance.client) | Q(person_customer=None)),
        Q(Q(state=form.instance.court_district.state) | Q(state=None)),
        Q(Q(court_district=form.instance.court_district) | Q(court_district=None)),
        Q(Q(city=(form.instance.movement.law_suit.organ.address_set.first().city if
                  form.instance.movement.law_suit.organ.address_set.first() else None)) | Q(city=None)))

    for rule in attachmentrules:
        attachments = Attachment.objects.filter(model_name='ecm.defaultattachmentrule').filter(object_id=rule.id)
        for attachment in attachments:
            obj = Ecm(path=attachment.file,
                      task=Task.objects.get(id=form.instance.id),
                      create_user_id=self.request.user.id,
                      create_date=timezone.now())
            obj.save()
