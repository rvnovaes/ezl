import copy
import uuid
from django.template.loader import render_to_string
from ecm.models import DefaultAttachmentRule, Attachment
from task.workflow import get_child_recipients
from task.models import *
from task.serializers import *
from task.mail import SendMail
from task.rules import RuleViewTask
from core.utils import get_office_session
from core.tasks import send_mail
from django.db.models import Q
from django.core.files.base import ContentFile
from django.conf import settings
from retrying import retry
import traceback
import logging
logger = logging.getLogger(__name__)


def get_task_attachment(self, form):
    state = form.instance.court_district.state if form.instance.court_district else None
    attachmentrules = DefaultAttachmentRule.objects.filter(
        Q(office=get_office_session(self.request)),
        Q(Q(type_task=form.instance.type_task) | Q(type_task=None)),
        Q(Q(person_customer=form.instance.client) | Q(person_customer=None)),
        Q(Q(state=state) | Q(state=None)),
        Q(
            Q(court_district=form.instance.court_district)
            | Q(court_district=None)),
        Q(
            Q(
                city=(form.instance.movement.law_suit.organ.address_set.
                      first().city if form.instance.movement and form.instance.
                      movement.law_suit and form.instance.movement.law_suit.
                      organ and form.instance.movement.law_suit.organ.
                      address_set.first() else None)) | Q(city=None)))

    for rule in attachmentrules:
        attachments = Attachment.objects.filter(
            model_name='ecm.defaultattachmentrule').filter(object_id=rule.id)
        for attachment in attachments:
            new_file = get_file_content_copy(attachment.file)
            if new_file:
                file_name = os.path.basename(attachment.file.name)
                new_file.name = file_name
                if not Ecm.objects.filter(
                        exhibition_name=file_name, task_id=form.instance.id):
                    obj = Ecm(
                        path=new_file,
                        task=Task.objects.get(id=form.instance.id),
                        create_user_id=self.request.user.id,
                        create_date=timezone.now(),
                        exhibition_name=file_name)
                    obj.save()


def get_file_content_copy(filefield):
    local_file_path = os.path.join(settings.MEDIA_ROOT, filefield.name)
    if os.path.exists(local_file_path):
        with open(local_file_path, 'rb') as local_file:
            content = ContentFile(local_file.read())
    else:
        try:
            content = ContentFile(filefield.read())
        except:
            content = None
    return content


def task_send_mail(instance, number, project_link, short_message, custom_text,
                   mail_list):
    mail = SendMail()
    mail.subject = 'Easy Lawyer - OS {} - {} - Prazo: {} - {}'.format(
        number,
        str(instance.type_task).title(),
        instance.final_deadline_date.strftime('%d/%m/%Y'),
        instance.task_status)
    mail.message = render_to_string(
        'mail/base.html', {
            'server': project_link,
            'pk': instance.pk,
            'project_name': settings.PROJECT_NAME,
            'number': str(number),
            'short_message': short_message,
            'custom_text': custom_text,
            'task': instance
        })
    mail.to_mail = list(set(mail_list))
    try:
        mail.send()
    except Exception as e:
        print(e)
        print('Você tentou mandar um e-mail')


def get_dashboard_tasks(request, office_session, checker, person):
    rule_view = RuleViewTask(request=request)
    dynamic_query = rule_view.get_dynamic_query(person, checker)
    data = Task.objects.none()
    exclude_status = []

    if not office_session:
        return data, office_session
    # NOTE: Quando o usuário é superusuário ou não possui permissão é retornado um objeto Q vazio
    if dynamic_query or checker.has_perm('group_admin', office_session):
        # filtra as OS de acordo com a pessoa (correspondente, solicitante e contratante) preenchido na OS
        if office_session:
            if not office_session.use_service:
                exclude_status.append(TaskStatus.ACCEPTED_SERVICE.value)
                exclude_status.append(TaskStatus.REFUSED_SERVICE.value)
            if not office_session.use_etl:
                exclude_status.append(TaskStatus.ERROR.value)
            data = Task.objects.filter(dynamic_query).filter(
                is_active=True, office_id=office_session.id).filter(~Q(
                    task_status__in=exclude_status))

    return data, exclude_status


def create_default_type_tasks(office, create_user=None):
    if not create_user:
        create_user = office.create_user
    main_type_tasks = TypeTaskMain.objects.all()
    TypeTask.objects.filter(office=office).delete()
    for main_type_task in main_type_tasks:
        type_task = TypeTask()
        type_task.name = main_type_task.name
        type_task.create_user = create_user
        type_task.office = office
        type_task.save()
        type_task.type_task_main.add(main_type_task)
        type_task.save()


def get_task_ecms(task_id):
    return Ecm.objects.filter(Q(tasks__id=task_id) | Q(task_id=task_id)).distinct('id')


def create_ecm_task(ecm, task):
    EcmTask.objects.get_or_create(ecm=ecm, task=task)


def clone_task_ecms(task_from, task_to):
    for ecm in get_task_ecms(task_from.id):
        create_ecm_task(ecm, task_to)


def self_or_none(obj):
    return obj if obj else None


def delegate_child_task(object_parent, office_correspondent):
    """
    Este metodo e chamado quando um escritorio delega uma OS para outro escritorio
    Ao realizar este processo a nova OS criada devera ficar com o status de Solicitada
    enquanto a OS pai devera ficar com o status de Delegada/Em Aberti
    :param object_parent: Task que sera copiada para gerar a nova task
    :param office_correspondent: Escritorio responsavel pela nova task
    :return:
    """
    if object_parent.get_child:
        if TaskStatus(object_parent.get_child.task_status) not in [
                TaskStatus.REFUSED, TaskStatus.REFUSED_SERVICE,
                TaskStatus.FINISHED
        ]:
            return False
    new_task = copy.copy(object_parent)
    new_task.task_hash = uuid.uuid4()
    new_task.legacy_code = None
    new_task.system_prefix = None
    new_task.pk = new_task.task_number = None
    new_task.person_asked_by = None
    new_task.person_executed_by = None
    new_task.person_distributed_by = None
    new_task.delegation_date = None
    new_task.office = office_correspondent
    new_task.task_status = TaskStatus.REQUESTED
    new_task.parent = object_parent
    new_task._mail_attrs = get_child_recipients(TaskStatus.OPEN)
    new_task.save()
    clone_task_ecms(object_parent, new_task)


def get_offices_to_pay(tasks):
    return [OfficeToPaySerializer(task.office).data for task in tasks]    

def get_clients_to_pay():
    pass
