import json
import csv
import os
import copy
from urllib.parse import urlparse
import pickle
from pathlib import Path
from django.contrib import messages
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import CustomLoginRequiredView
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db import IntegrityError, OperationalError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin
from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, \
    operational_error_create, ioerror_create, exception_create, \
    integrity_error_delete, \
    DELETE_EXCEPTION_MESSAGE, success_sent, success_delete, NO_PERMISSIONS_DEFINED, record_from_wrong_office
from core.models import Person
from core.views import AuditFormMixin, MultiDeleteViewMixin, SingleTableViewMixin
from etl.models import InconsistencyETL
from etl.tables import DashboardErrorStatusTable
from lawsuit.models import Movement, CourtDistrict
from task.filters import TaskFilter, TaskToPayFilter, TaskToReceiveFilter
from task.forms import TaskForm, TaskDetailForm, TaskCreateForm, TaskToAssignForm, FilterForm
from task.models import Task, TaskStatus, Ecm, TypeTask, TaskHistory, DashboardViewModel, Filter, TaskFeedback, \
    TaskGeolocation
from task.signals import send_notes_execution_date
from task.tables import TaskTable, DashboardStatusTable, FilterTable
from task.workflow import get_child_recipients
from financial.models import ServicePriceTable
from survey.models import SurveyPermissions
from financial.tables import ServicePriceTableTaskTable
from core.utils import get_office_session, get_domain
from ecm.models import DefaultAttachmentRule, Attachment
from task.utils import get_task_attachment
from decimal import Decimal
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_groups_with_perms
from django.core.files.base import ContentFile


class TaskListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = Task
    table_class = TaskTable


class TaskBulkCreateView(AuditFormMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    success_url = reverse_lazy('task_list')
    success_message = CREATE_SUCCESS_MESSAGE
    template_name_suffix = '_bulk_create_form'

    def form_valid(self, form):
        task = form.instance
        form.instance.movement_id = self.request.POST['movement']
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        form.instance.__server = get_domain(self.request)
        response = super(TaskBulkCreateView, self).form_valid(form)

        if form.cleaned_data['documents']:
            for document in form.cleaned_data['documents']:
                file_name = document.name.replace(' ', '_')
                task.ecm_set.create(path=document,
                                    exhibition_name=file_name,
                                    create_user=task.create_user)

        form.delete_temporary_files()

        return response

    def get_success_url(self):
        return "{}?movement={}&movementLabel={}&lawsuit={}&lawsuitLabel={}&folder={}&folderLabel={}".format(
            reverse('task_add'),
            self.object.movement_id,
            self.object.movement.type_movement.name,
            self.object.movement.law_suit_id,
            self.object.movement.law_suit,
            self.object.movement.law_suit.folder_id,
            self.object.movement.law_suit.folder,
        )


class TaskCreateView(AuditFormMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    success_message = CREATE_SUCCESS_MESSAGE
    template_name_suffix = '_persist_form'

    def get_initial(self):
        if self.kwargs.get('movement'):
            lawsuit_id = Movement.objects.get(id=self.kwargs.get('movement')).law_suit_id
            self.kwargs['lawsuit'] = lawsuit_id

        if isinstance(self, CreateView):
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True

        elif isinstance(self, UpdateView):
            self.form_class.declared_fields['is_active'].disabled = False

        return self.initial.copy()

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_valid(self, form):
        task = form.instance
        form.instance.movement_id = self.kwargs.get('movement')
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        form.instance.__server = get_domain(self.request)

        response = super(TaskCreateView, self).form_valid(form)
        if form.cleaned_data['documents']:
            for document in form.cleaned_data['documents']:
                file_name = document.name.replace(' ', '_')
                task.ecm_set.create(path=document,
                                    exhibition_name=file_name,
                                    create_user=task.create_user)

        form.delete_temporary_files()

        return response

    def get_success_url(self):
        return reverse('movement_update',
                       kwargs={'lawsuit': self.kwargs['lawsuit'],
                               'pk': self.kwargs['movement']})


class TaskToAssignView(AuditFormMixin, UpdateView):
    model = Task
    form_class = TaskToAssignForm
    success_url = reverse_lazy('dashboard')
    template_name_suffix = '_to_assign'

    def form_valid(self, form):
        super().form_valid(form)
        if form.is_valid():
            if not form.instance.person_distributed_by:
                form.instance.person_distributed_by = self.request.user.person
            form.instance.task_status = TaskStatus.OPEN
            # TODO: rever processo de anexo, quando for trocar para o ECM Generico
            get_task_attachment(self, form)
            form.save()
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def form_invalid(self, form):
        super().form_invalid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))


class TaskUpdateView(AuditFormMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_persist_form'

    def get_initial(self):
        if self.kwargs.get('movement'):
            lawsuit_id = Movement.objects.get(id=self.kwargs.get('movement')).law_suit_id
            self.kwargs['lawsuit'] = lawsuit_id
            self.success_url = reverse('movement_update', kwargs={'lawsuit': self.kwargs['lawsuit'],
                                                                  'pk': self.kwargs['movement']})
        if isinstance(self, CreateView):
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True

        elif isinstance(self, UpdateView):
            self.form_class.declared_fields['is_active'].disabled = False
        return self.initial.copy()

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_valid(self, form):
        task = form.instance
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        form.instance.__server = get_domain(self.request)
        super(TaskUpdateView, self).form_valid(form)

        if form.cleaned_data['documents']:
            for document in form.cleaned_data['documents']:
                file_name = document.name.replace(' ', '_')
                task.ecm_set.create(path=document,
                                    exhibition_name=file_name,
                                    create_user=task.create_user)

        form.delete_temporary_files()
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)

        return context


class TaskDeleteView(SuccessMessageMixin, CustomLoginRequiredView, MultiDeleteViewMixin):
    model = Task
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)

    def post(self, request, *args, **kwargs):
        self.success_url = urlparse(request.META.get('HTTP_REFERER')).path
        return super(TaskDeleteView, self).post(request, *args, **kwargs)


class TaskReportBase(PermissionRequiredMixin, CustomLoginRequiredView, TemplateView):
    permission_required = ('core.view_all_tasks', )
    template_name = None
    filter_class = None
    datetime_field = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        self.task_filter = self.filter_class(data=self.request.GET, request=self.request)
        context['filter'] = self.task_filter
        context['offices_report'] = self.get_os_grouped_by_office()
        context['total'] = sum(map(lambda x: x['total'], context['offices_report']))
        return context

    def get_queryset(self):
        office = get_office_session(self.request)
        queryset = Task.objects.filter(
            office=office,
            task_status=TaskStatus.FINISHED,
            child__isnull=False
        )
        queryset = self.filter_queryset(queryset)
        return queryset.order_by('child__office__name')

    def filter_queryset(self, queryset):
        if not self.task_filter.form.is_valid():
            messages.add_message(self.request, messages.ERROR, 'Formulário inválido.')
        else:
            data = self.task_filter.form.cleaned_data
            query = Q()
            finished_query = Q()

            if data['status']:
                key = "{}__isnull".format(self.datetime_field)
                query.add(Q(**{key: data['status'] != 'true'}), Q.AND)

            if data['client']:
                query.add(Q(movement__law_suit__folder__person_customer__legal_name__unaccent__icontains=data['client']), Q.AND)

            if data['office']:
                if isinstance(self, ToReceiveTaskReportView):
                    query.add(Q(parent__office__name__unaccent__icontains=data['office']), Q.AND)
                else:
                    query.add(Q(office__name__unaccent__icontains=data['office']), Q.AND)

            if data['finished_in']:
                if data['finished_in'].start:
                    finished_query.add(
                        Q(finished_date__gte=data['finished_in'].start.replace(hour=0, minute=0)), Q.AND)
                if data['finished_in'].stop:
                    finished_query.add(
                        Q(finished_date__lte=data['finished_in'].stop.replace(hour=23, minute=59)), Q.AND)
            else:
                # O filtro padrão para finished_date é do dia 01 do mês atual e o dia corrente como data final
                finished_query.add(
                    Q(finished_date__gte=timezone.now().replace(day=1, hour=0, minute=0)), Q.AND)
                finished_query.add(
                    Q(finished_date__lte=timezone.now().replace(hour=23, minute=59)), Q.AND)
            query.add(Q(finished_query), Q.AND)
            queryset = queryset.filter(query)

        return queryset

    def get_os_grouped_by_office(self):
        offices = []
        offices_map = {}
        tasks = self.get_queryset()
        for task in tasks:
            correspondent = self._get_related_office(task)
            if correspondent not in offices_map:
                offices_map[correspondent] = []
            offices_map[correspondent].append(task)

        for office, tasks in offices_map.items():
            tasks.sort(key=lambda x: x.client.name)
            offices.append({
                "name": office.name,
                "tasks": tasks,
                "total": sum(map(lambda x: x.amount, tasks))
                })

        return offices


class ToReceiveTaskReportView(TaskReportBase):
    template_name = 'task/reports/to_receive.html'
    filter_class = TaskToReceiveFilter
    datetime_field = 'receipt_date'

    def get_queryset(self):
        office = get_office_session(self.request)
        queryset = Task.objects.filter(
            office=office,
            task_status=TaskStatus.FINISHED,
            parent__isnull=False
        )
        queryset = self.filter_queryset(queryset)
        return queryset.order_by('parent__office__name')

    def _get_related_office(self, task):
        return task.parent.office

    def post(self, request):
        office = get_office_session(self.request)
        tasks_payload = request.POST.get('tasks')
        if not tasks_payload:
            return JsonResponse({"error": "tasks is required"}, status=400)

        for task_id in json.loads(tasks_payload):
            task = Task.objects.get(id=task_id, office=office)
            setattr(task, self.datetime_field, timezone.now())
            task.save()

        messages.add_message(self.request, messages.INFO, "OS's marcadas como recebidas com sucesso.")
        return JsonResponse({"status": "ok"})


class ToPayTaskReportView(TaskReportBase):
    template_name = 'task/reports/to_pay.html'
    filter_class = TaskToPayFilter
    datetime_field = 'billing_date'

    def get_queryset(self):        
        office = get_office_session(self.request)
        queryset = Task.objects.filter(
            parent__office=office,
            task_status=TaskStatus.FINISHED,
            parent__isnull=False
        )
        queryset = self.filter_queryset(queryset)
        return queryset.order_by('child__office__name')

    def _get_related_office(self, task):
        return task.office

    def post(self, request):
        office = get_office_session(self.request)
        tasks_payload = request.POST.get('tasks')
        if not tasks_payload:
            return JsonResponse({"error": "tasks is required"}, status=400)

        for task_id in json.loads(tasks_payload):
            task = Task.objects.get(id=task_id, parent__office=office)
            setattr(task, self.datetime_field, timezone.now())
            task.save()

        messages.add_message(self.request, messages.INFO, "OS's faturadas com sucesso.")
        return JsonResponse({"status": "ok"})


class DashboardView(CustomLoginRequiredView, MultiTableMixin, TemplateView):
    template_name = 'task/task_dashboard.html'
    table_pagination = {
        'per_page': 5
    }
    count_task = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        person = Person.objects.get(auth_user=self.request.user)
        context['task_count'] = self.count_task

        if not self.request.user.get_all_permissions():
            context['messages'] = [
                {'tags': 'error', 'message': NO_PERMISSIONS_DEFINED}
            ]
        return context

    def get_tables(self):
        person = Person.objects.get(auth_user=self.request.user)
        data, data_error, office_session = self.get_data(person)
        self.set_count_task(data, data_error)
        tables = self.get_list_tables(data, data_error, person, office_session) if person else []
        return tables

    def set_count_task(self, data, data_error):
        self.count_task = len(data) + len(data_error)

    def get_data(self, person):
        checker = ObjectPermissionChecker(person.auth_user)
        dynamic_query = self.get_dynamic_query(person, checker)
        data = []
        data_error = []
        office_session = get_office_session(self.request)
        if not office_session:
            return data, data_error, office_session
        # NOTE: Quando o usuário é superusuário ou não possui permissão é retornado um objeto Q vazio
        if dynamic_query or checker.has_perm('group_admin', office_session):
            # filtra as OS de acordo com a pessoa (correspondente, solicitante e contratante) preenchido na OS
            if office_session:
                data = DashboardViewModel.objects.filter(office_id=office_session.id).filter(dynamic_query)
                data_error = DashboardViewModel.objects.filter(office_id=office_session.id).filter(dynamic_query,
                                                                                                   task_status=TaskStatus.ERROR)
        return data, data_error, office_session

    @staticmethod
    def get_list_tables(data, data_error, person, office_session):
        grouped = dict()
        for obj in data:
            grouped.setdefault(TaskStatus(obj.task_status), []).append(obj)
        returned = grouped.get(TaskStatus.RETURN) or {}
        accepted = grouped.get(TaskStatus.ACCEPTED) or {}
        opened = grouped.get(TaskStatus.OPEN) or {}
        done = grouped.get(TaskStatus.DONE) or {}
        refused = grouped.get(TaskStatus.REFUSED) or {}
        blocked_payment = grouped.get(TaskStatus.BLOCKEDPAYMENT) or {}
        finished = grouped.get(TaskStatus.FINISHED) or {}
        requested = grouped.get(TaskStatus.REQUESTED) or {}
        accepted_service = grouped.get(TaskStatus.ACCEPTED_SERVICE) or {}
        refused_service = grouped.get(TaskStatus.REFUSED_SERVICE) or {}
        #  Necessario filtrar as inconsistencias pelos ids das tasks pelo fato das instancias de error serem de DashboardTaskView
        error = InconsistencyETL.objects.filter(is_active=True, task__id__in=[task.pk for task in data_error]) or {}

        return_list = []
        checker = ObjectPermissionChecker(person.auth_user)
        if not office_session:
            return []
        if checker.has_perm('can_access_general_data', office_session) or checker.has_perm('group_admin',
                                                                                           office_session):
            return_list.append(DashboardErrorStatusTable(error,
                                                         title='Erro no sistema de origem',
                                                         status=TaskStatus.ERROR))

            # status 10 - Solicitada
            return_list.append(DashboardStatusTable(requested,
                                                    title='Solicitadas',
                                                    status=TaskStatus.REQUESTED))
            # status 11 - Aceita pelo Service
            return_list.append(DashboardStatusTable(accepted_service,
                                                    title='Aceitas pelo Service',
                                                    status=TaskStatus.ACCEPTED_SERVICE))

            # status 20 - Recusada pelo Sevice
            return_list.append(DashboardStatusTable(refused_service,
                                                    title='Recusadas pelo Service',
                                                    status=TaskStatus.REFUSED_SERVICE))

        return_list.append(DashboardStatusTable(returned,
                                                title='Retornadas',
                                                status=TaskStatus.RETURN))

        return_list.append(DashboardStatusTable(opened,
                                                title='Delegada/Em Aberto',
                                                status=TaskStatus.OPEN))

        return_list.append(DashboardStatusTable(accepted,
                                                title='A Cumprir',
                                                status=TaskStatus.ACCEPTED))

        return_list.append(DashboardStatusTable(done,
                                                title='Cumpridas',
                                                status=TaskStatus.DONE))

        return_list.append(DashboardStatusTable(finished,
                                                title='Finalizadas',
                                                status=TaskStatus.FINISHED))

        # status 40 - Recusada
        return_list.append(DashboardStatusTable(refused,
                                                title='Recusadas',
                                                status=TaskStatus.REFUSED))

        return_list.append(DashboardStatusTable(blocked_payment,
                                                title='Glosadas',
                                                status=TaskStatus.BLOCKEDPAYMENT))

        return return_list

    @staticmethod
    def get_query_all_tasks(person):
        return Q()

    @staticmethod
    def get_query_delegated_tasks(person):
        return Q(person_executed_by=person.id)

    @staticmethod
    def get_query_requested_tasks(person):
        return Q(person_asked_by=person.id)

    @staticmethod
    def get_query_distributed_tasks(person):
        return Q(task_status=TaskStatus.REQUESTED) | Q(task_status=TaskStatus.ERROR) | Q(
            person_distributed_by=person.id)

    def get_dynamic_query(self, person, checker):
        dynamic_query = Q()
        office_session = get_office_session(self.request)
        if office_session:
            if checker.has_perm('view_all_tasks', office_session):
                return self.get_query_all_tasks(person)
            permissions_to_check = {
                'view_all_tasks': self.get_query_all_tasks,
                'view_delegated_tasks': self.get_query_delegated_tasks,
                'view_distributed_tasks': self.get_query_distributed_tasks,
                'view_requested_tasks': self.get_query_requested_tasks
            }
            for permission in checker.get_perms(office_session):
                if permission in permissions_to_check.keys():
                    dynamic_query |= permissions_to_check.get(permission)(person)
        return dynamic_query


class TaskDetailView(SuccessMessageMixin, CustomLoginRequiredView, UpdateView):
    model = Task
    form_class = TaskDetailForm
    success_url = reverse_lazy('dashboard')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name = 'task/task_detail.html'

    def form_valid(self, form):
        if TaskStatus[self.request.POST['action']] == TaskStatus.OPEN \
                and not form.cleaned_data['servicepricetable_id']:
            form.is_valid = False
            messages.error(self.request, "Favor Selecionar um correspondente")
            return self.form_invalid(form)
        form.instance.task_status = TaskStatus[self.request.POST['action']] or TaskStatus.INVALID
        form.instance.alter_user = User.objects.get(id=self.request.user.id)
        notes = form.cleaned_data['notes'] if form.cleaned_data['notes'] else None
        execution_date = (form.cleaned_data['execution_date']
                          if form.cleaned_data['execution_date'] else form.initial['execution_date'])
        survey_result = (form.cleaned_data['survey_result']
                         if form.cleaned_data['survey_result'] else form.initial['survey_result'])

        send_notes_execution_date.send(sender=self.__class__, notes=notes, instance=form.instance,
                                       execution_date=execution_date, survey_result=survey_result)
        form.instance.__server = get_domain(self.request)
        if form.instance.task_status == TaskStatus.ACCEPTED_SERVICE:
            form.instance.person_distributed_by = self.request.user.person
        if form.instance.task_status == TaskStatus.REFUSED_SERVICE:
            form.instance.person_distributed_by = self.request.user.person
        if form.instance.task_status == TaskStatus.OPEN:
            if not form.instance.person_distributed_by:
                form.instance.person_distributed_by = self.request.user.person
            default_amount = Decimal('0.00') if not form.instance.amount else form.instance.amount
            form.instance.amount = (form.cleaned_data['amount'] if form.cleaned_data['amount'] else default_amount)
            servicepricetable_id = (
                self.request.POST['servicepricetable_id'] if self.request.POST['servicepricetable_id'] else None)
            servicepricetable = ServicePriceTable.objects.filter(id=servicepricetable_id).first()
            get_task_attachment(self, form)
            if servicepricetable:
                self.delegate_child_task(form.instance, servicepricetable.office_correspondent)
                form.instance.person_executed_by = None

        feedback_rating = form.cleaned_data.get('feedback_rating')
        feedback_comment = form.cleaned_data.get('feedback_comment')
        if feedback_rating and not form.instance.taskfeedback_set.exists():
            TaskFeedback.objects.create(
                task=form.instance,
                rating=feedback_rating,
                comment=feedback_comment,
                create_user=form.instance.alter_user)

        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)
        context['task_history'] = \
            TaskHistory.objects.filter(task_id=self.object.id).order_by('-create_date')
        context['survey_data'] = (self.object.type_task.survey.data
                                  if self.object.type_task.survey else None)

        type_task = self.object.type_task
        court_district = self.object.movement.law_suit.court_district
        state = self.object.movement.law_suit.court_district.state
        client = self.object.movement.law_suit.folder.person_customer
        context['correspondents_table'] = ServicePriceTableTaskTable(
            ServicePriceTable.objects.filter(Q(office=self.object.office) | Q(office__public_office=True),
                                             Q(office_correspondent__is_active=True),
                                             Q(Q(type_task=type_task) | Q(type_task=None)),
                                             Q(Q(court_district=court_district) | Q(court_district=None)),
                                             Q(Q(state=state) | Q(state=None)),
                                             Q(Q(client=client) | Q(client=None)))
        )
        return context

    @staticmethod
    def delegate_child_task(object_parent, office_correspondent):
        """
        Este metodo e chamado quando um escritorio delega uma OS para outro escritorio
        Ao realizar este processo a nova OS criada devera ficar com o status de Solicitada
        enquanto a OS pai devera ficar com o status de Delegada/Em Aberti
        :param object_parent: Task que sera copiada para gerar a nova task
        :param office_correspondent: Escritorio responsavel pela nova task
        :return:
        """
        new_task = copy.copy(object_parent)
        new_task.legacy_code = None
        new_task.system_prefix = None
        new_task.pk = new_task.task_number = None
        new_task.person_asked_by = None
        new_task.person_executed_by = None
        new_task.person_distributed_by = None
        new_task.office = office_correspondent
        new_task.task_status = TaskStatus.REQUESTED
        new_task.parent = object_parent
        new_type_task = TypeTask.objects.filter(
            name=object_parent.type_task.name, survey=object_parent.type_task.survey).latest('pk')
        new_task.type_task = new_type_task
        new_task._mail_attrs = get_child_recipients(TaskStatus.OPEN)
        new_task.save()
        for ecm in object_parent.ecm_set.all():
            if Path(ecm.path.path).is_file():
                new_file = ContentFile(ecm.path.read())
                new_file.name = os.path.basename(ecm.path.name)
                new_ecm = copy.copy(ecm)
                new_ecm.pk = None
                new_ecm.exhibition_name = new_file.name
                new_ecm.task = new_task
                new_ecm.path = new_file
                new_ecm.ecm_related = ecm
                new_ecm.save()

    def dispatch(self, request, *args, **kwargs):        
        res = super().dispatch(request, *args, **kwargs)        
        office_session = get_office_session(request)
        if office_session != Task.objects.filter(pk=kwargs.get('pk')).first().office:
            messages.error(self.request, "A OS que está tentando acessar, não pertence ao escritório selecionado."
                                         " Favor selecionar o escritório correto")
            if request.session.get('custom_session_user'):
                del request.session['custom_session_user']
                request.session.modified = True
            return HttpResponseRedirect(reverse('office_instance'))
        return res


class EcmCreateView(CustomLoginRequiredView, CreateView):
    def post(self, request, *args, **kwargs):

        files = request.FILES.getlist('path')
        task = kwargs['pk']
        data = {'success': False,
                'message': exception_create()}

        for file in files:
            file_name = file._name.replace(' ', '_')
            obj_task = Task.objects.get(id=task)
            ecm = Ecm(path=file,
                      task=obj_task,
                      exhibition_name=file_name,
                      create_user_id=str(request.user.id),
                      create_date=timezone.now())

            try:
                ecm.save()
                data = {'success': True,
                        'id': ecm.id,
                        'name': str(file),
                        'user': str(self.request.user),
                        'username': str(self.request.user.first_name + ' ' +
                                        self.request.user.last_name),
                        'filename': str(ecm.exhibition_name),
                        'task_id': str(task),
                        'message': success_sent()
                        }

            except OperationalError:
                data = {'success': False,
                        'message': operational_error_create()}

            except IOError:

                data = {'is_deleted': False,
                        'message': ioerror_create()}

            except Exception:
                data = {'success': False,
                        'message': exception_create()}

        return JsonResponse(data)


@login_required
def delete_ecm(request, pk):
    query = Ecm.objects.filter(id=pk)
    task = query.values('task_id').first()

    try:
        query.delete()
        num_ged = Ecm.objects.filter(task_id=task['task_id']).count()
        data = {'is_deleted': True,
                'num_ged': num_ged,
                'message': success_delete()
                }

    except IntegrityError:
        data = {'is_deleted': False,
                'message': integrity_error_delete()
                }
    except Exception:
        data = {'is_deleted': False,
                'message': DELETE_EXCEPTION_MESSAGE,
                }

    return JsonResponse(data)


class DashboardSearchView(CustomLoginRequiredView, SingleTableView):
    model = DashboardViewModel
    filter_class = TaskFilter
    template_name = 'task/task_filter.html'
    context_object_name = 'task_filter'
    context_filter_name = 'filter'
    ordering = ['-final_deadline_date']
    table_class = DashboardStatusTable

    def query_builder(self):
        query_set = {}
        person_dynamic_query = Q()
        person = Person.objects.get(auth_user=self.request.user)
        office_session = get_office_session(self.request)
        checker = ObjectPermissionChecker(person.auth_user)

        filters = self.request.GET
        task_filter = TaskFilter(data=filters, request=self.request)
        task_form = task_filter.form

        if task_form.is_valid():
            data = task_form.cleaned_data

            if data['custom_filter']:
                q = pickle.loads(data['custom_filter'].query)
                query_set = DashboardViewModel.objects.filter(q)

            else:
                task_dynamic_query = Q()
                client_query = Q()
                requested_dynamic_query = Q()
                accepted_service_dynamic_query = Q()
                refused_service_query = Q()
                open_dynamic_query = Q()
                accepted_dynamic_query = Q()
                refused_dynamic_query = Q()
                return_dynamic_query = Q()
                done_dynamic_query = Q()
                blocked_payment_dynamic_query = Q()
                finished_dynamic_query = Q()

                if not checker.has_perm('can_distribute_tasks', office_session):
                    if checker.has_perm('view_delegated_tasks', office_session):
                        person_dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
                    if checker.has_perm('view_requested_tasks', office_session):
                        person_dynamic_query.add(Q(person_asked_by=person.id), Q.AND)

                if data['state']:
                    task_dynamic_query.add(Q(movement__law_suit__court_district__state=data['state']), Q.AND)
                if data['court_district']:
                    task_dynamic_query.add(Q(movement__law_suit__court_district=data['court_district']), Q.AND)
                if data['type_task']:
                    task_dynamic_query.add(Q(type_task=data['type_task']), Q.AND)
                if data['court']:
                    task_dynamic_query.add(Q(movement__law_suit__organ=data['court']), Q.AND)
                if data['cost_center']:
                    task_dynamic_query.add(Q(movement__law_suit__folder__cost_center=data['cost_center']), Q.AND)
                if data['folder_number']:
                    task_dynamic_query.add(Q(movement__law_suit__folder__folder_number=data['folder_number']), Q.AND)
                if data['folder_legacy_code']:
                    task_dynamic_query.add(Q(movement__law_suit__folder__legacy_code=data['folder_legacy_code']), Q.AND)
                if data['client']:
                    task_dynamic_query.add(Q(movement__law_suit__folder__person_customer__id=data['client']), Q.AND)
                if data['law_suit_number']:
                    task_dynamic_query.add(Q(movement__law_suit__law_suit_number=data['law_suit_number']), Q.AND)
                if data['task_number']:
                    task_dynamic_query.add(Q(task_number=data['task_number']), Q.AND)
                if data['task_origin_code']:
                    task_dynamic_query.add(Q(Q(legacy_code=data['task_origin_code'])|\
                        Q(parent_task_number=data['task_origin_code'])), Q.AND)
                if data['person_executed_by']:
                    task_dynamic_query.add(Q(person_executed_by=data['person_executed_by']), Q.AND)
                if data['person_asked_by']:
                    task_dynamic_query.add(Q(person_asked_by=data['person_asked_by']), Q.AND)
                if data['person_distributed_by']:
                    task_dynamic_query.add(Q(person_distributed_by=data['person_distributed_by']), Q.AND)
                if data['requested_in']:
                    if data['requested_in'].start:
                        requested_dynamic_query.add(
                            Q(requested_date__gte=data['requested_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['requested_in'].stop:
                        requested_dynamic_query.add(
                            Q(requested_date__lte=data['requested_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['accepted_service_in']:
                    if data['accepted_service_in'].start:
                        accepted_service_dynamic_query.add(
                            Q(acceptance_service_date__gte=data['accepted_service_in'].start.replace(hour=0, minute=0)),
                            Q.AND)
                    if data['accepted_service_in'].stop:
                        accepted_service_dynamic_query.add(
                            Q(acceptance_service_date__lte=data['accepted_service_in'].stop.replace(hour=23,
                                                                                                    minute=59)), Q.AND)
                if data['refused_service_in']:
                    if data['refused_service_in'].start:
                        refused_service_query.add(
                            Q(refused_service_date__gte=data['refused_service_in'].start.replace(hour=0, minute=0)),
                            Q.AND)
                    if data['refused_service_in'].stop:
                        refused_service_query.add(
                            Q(refused_service_date__lte=data['refused_service_in'].stop.replace(hour=23, minute=59)),
                            Q.AND)
                if data['open_in']:
                    if data['open_in'].start:
                        open_dynamic_query.add(
                            Q(delegation_date__gte=data['open_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['open_in'].stop:
                        open_dynamic_query.add(
                            Q(delegation_date__lte=data['open_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['accepted_in']:
                    if data['accepted_in'].start:
                        accepted_dynamic_query.add(
                            Q(acceptance_date__gte=data['accepted_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['accepted_in'].stop:
                        accepted_dynamic_query.add(
                            Q(acceptance_date__lte=data['accepted_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['refused_in']:
                    if data['refused_in'].start:
                        refused_dynamic_query.add(
                            Q(refused_date__gte=data['refused_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['refused_in'].stop:
                        refused_dynamic_query.add(
                            Q(refused_date__lte=data['refused_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['return_in']:
                    if data['return_in'].start:
                        return_dynamic_query.add(
                            Q(return_date__gte=data['return_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['return_in'].stop:
                        return_dynamic_query.add(
                            Q(return_date__lte=data['return_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['done_in']:
                    if data['done_in'].start:
                        done_dynamic_query.add(
                            Q(execution_date__gte=data['done_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['done_in'].stop:
                        done_dynamic_query.add(
                            Q(execution_date__lte=data['done_in'].stop.replace(hour=23, minute=59)), Q.AND)
                if data['blocked_payment_in']:
                    if data['blocked_payment_in'].start:
                        blocked_payment_dynamic_query.add(
                            Q(blocked_payment_date__gte=data['blocked_payment_in'].start.replace(hour=0, minute=0)),
                            Q.AND)
                    if data['blocked_payment_in'].stop:
                        blocked_payment_dynamic_query.add(
                            Q(blocked_payment_date__lte=data['blocked_payment_in'].stop.replace(hour=23, minute=59)),
                            Q.AND)
                if data['finished_in']:
                    if data['finished_in'].start:
                        finished_dynamic_query.add(
                            Q(finished_date__gte=data['finished_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['finished_in'].stop:
                        finished_dynamic_query.add(
                            Q(finished_date__lte=data['finished_in'].stop.replace(hour=23, minute=59)), Q.AND)

                person_dynamic_query.add(Q(client_query), Q.AND) \
                    .add(Q(task_dynamic_query), Q.AND) \
                    .add(Q(requested_dynamic_query), Q.AND) \
                    .add(Q(accepted_service_dynamic_query), Q.AND) \
                    .add(Q(refused_service_query), Q.AND) \
                    .add(Q(open_dynamic_query), Q.AND) \
                    .add(Q(accepted_dynamic_query), Q.AND) \
                    .add(Q(refused_dynamic_query), Q.AND) \
                    .add(Q(return_dynamic_query), Q.AND) \
                    .add(Q(done_dynamic_query), Q.AND) \
                    .add(Q(blocked_payment_dynamic_query), Q.AND) \
                    .add(Q(finished_dynamic_query), Q.AND)

                office_id = (get_office_session(self.request).id if get_office_session(self.request) else 0)
                query_set = DashboardViewModel.objects.filter(office_id=office_id).filter(person_dynamic_query)

            try:
                if filters.get('save_filter', None) is not None:
                    filter_name = data['custom_filter_name']
                    filter_description = data['custom_filter_description']
                    q = pickle.dumps(person_dynamic_query)
                    new_filter = Filter(name=filter_name, query=q, description=filter_description,
                                        create_user=self.request.user, create_date=timezone.now())
                    new_filter.save()
            except IntegrityError:
                messages.add_message(self.request, messages.ERROR, 'Já existe filtro com este nome.')
        else:
            messages.add_message(self.request, messages.ERROR, 'Formulário inválido.')
        return query_set, task_filter

    def get_queryset(self, **kwargs):

        task_list, task_filter = self.query_builder()
        self.filter = task_filter

        return task_list

    def get_context_data(self, **kwargs):
        context = super(DashboardSearchView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        table = DashboardStatusTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get(self, request):
        checker = ObjectPermissionChecker(self.request.user)
        if (self.request.GET.get('export_answers') and
                checker.has_perm('can_view_survey_results', get_office_session(request))):
            return self._export_answers(request)

        return super().get(request)

    def _export_answers(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="respostas_dos_formularios.csv"'
        writer = csv.writer(response)

        queryset = self.get_queryset().filter(survey_result__isnull=False)
        tasks = self._fill_tasks_answers(queryset)
        columns = self._get_answers_columns(tasks)
        writer.writerow(['N° da OS', 'N° da OS no sistema de origem'] + columns)

        for task in tasks:
            self._export_answers_write_task(writer, task, columns)
        return response

    def _fill_tasks_answers(self, queryset):
        tasks = []
        for task in queryset:
            try:
                task.survey_result = json.loads(task.survey_result)
                tasks.append(task)
            except ValueError:
                return
        return tasks

    def _export_answers_write_task(self, writer, task, columns):
        base_fields = [task.id, task.legacy_code]
        answers = ['' for x in range(len(columns))]
        for question, answer in task.survey_result.items():
            question_index = columns.index(question)
            answers[question_index] = answer

        writer.writerow(base_fields + answers)

    def _get_answers_columns(self, tasks):
        columns = []
        i = 0
        for task in tasks:
            for question, answer in task.survey_result.items():
                if question not in columns:
                    columns.append(question)
        columns.sort()
        return columns


class DashboardStatusCheckView(CustomLoginRequiredView, View):

    def post(self, request, *args, **kwargs):
        tasks_payload = request.POST.get('tasks')
        if not tasks_payload:
            return JsonResponse({"error": "tasks is required"}, status=400)

        # Ordena as tasks para que possamos comparar o que está no banco com o que foi recebido
        tasks = sorted(json.loads(tasks_payload), key=lambda x: x[0])

        # Convertemos a lista para uma tupla de tuplas que é o formato que é retornado pelo banco
        tasks = tuple(map(lambda x: (x[0], x[1]), tasks))
        ids = map(lambda x: x[0], tasks)

        db_tasks = Task.objects.filter(id__in=ids).order_by('id').values_list('id', 'task_status')

        # Comparamos as tasks que foram enviadas com as que estão no banco para saber se houve mudanças
        has_changed = tuple(db_tasks) != tasks
        return JsonResponse({"has_changed": has_changed})


@login_required
def ajax_get_task_data_table(request):
    status = request.GET.get('status')
    xdata = []
    checker = ObjectPermissionChecker(request.user)
    dash = DashboardView()
    dash.request = request
    dynamic_query = dash.get_dynamic_query(request.user.person, checker)
    query = DashboardViewModel.objects.filter(dynamic_query).filter(is_active=True, task_status=status,
                                                                    office=get_office_session(request))
    if status == str(TaskStatus.ERROR):
        query_error = InconsistencyETL.objects.filter(is_active=True,
                                                      task__id__in=list(query.values_list('id', flat=True)))
        xdata.append(
            list(
                map(lambda x: [
                    x.task.pk,
                    x.task.task_number,
                    timezone.localtime(x.task.final_deadline_date).strftime('%d/%m/%Y %H:%M') if x.task.final_deadline_date else '',
                    x.task.type_task.name,
                    x.task.lawsuit_number,
                    x.task.court_district.name,
                    x.task.court_district.state.initials,
                    x.task.client.name,
                    x.task.opposing_party,
                    timezone.localtime(x.task.delegation_date).strftime('%d/%m/%Y %H:%M') if x.task.delegation_date else '',
                    x.task.origin_code,
                    x.inconsistency,
                    x.solution,
                ], query_error)
            )
        )
    else:
        xdata.append(
            list(
                map(lambda x: [
                    x.pk,
                    x.task_number,
                    timezone.localtime(x.final_deadline_date).strftime('%d/%m/%Y %H:%M') if x.final_deadline_date else '',
                    x.type_service,
                    x.lawsuit_number,
                    x.court_district.name,
                    x.court_district.state.initials,
                    x.client,
                    x.opposing_party,
                    timezone.localtime(x.delegation_date).strftime('%d/%m/%Y %H:%M') if x.delegation_date else '',
                    x.origin_code,
                    '',
                    '',
                ], query)
            )
        )

    data = {
        "data": xdata[0]
    }
    return JsonResponse(data)


def ajax_get_ecms(request):
    task_id = request.GET.get('task_id')
    data_list = []
    ecms = Ecm.objects.filter(task_id=task_id)
    for ecm in ecms:
        data_list.append({
            'task_id': ecm.task_id,
            'pk': ecm.pk,
            'url': ecm.path.name,
            'filename': ecm.filename,
            'exhibition_name': ecm.exhibition_name if ecm.exhibition_name else ecm.filename,
            'user': ecm.create_user.username,
            'data': timezone.localtime(ecm.create_date).strftime('%d/%m/%Y %H:%M'),
            'state': ecm.task.get_task_status_display(),
        })
    data = {
        'task_id': task_id,
        'total_ecms': ecms.count(),
        'ecms': data_list
    }
    return JsonResponse(data)


class FilterListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = Filter
    table_class = FilterTable

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data para retornar apenas filtros criados pelo usuário logado
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        context = super(FilterListView, self).get_context_data(**kwargs)
        checker = ObjectPermissionChecker(self.request.user)
        if not checker.has_perm('group_admin', get_office_session(self.request)):
            context['table'] = self.table_class(context['table'].data.data.filter(create_user=self.request.user))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(context['table'])
        return context


class FilterUpdateView(AuditFormMixin, UpdateView):
    model = Filter
    form_class = FilterForm
    success_url = reverse_lazy('filter_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super().get_context_data(**kwargs)
        cache.set('filter_page', self.request.META.get('HTTP_REFERER'))
        return context

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o metodo post e verifica se existe cache da ultima url
        Isso e necessario pelo fato da necessidade de retornar pra mesma paginacao
        Que o usuario se encontrava ao fazer a alteracao
        :param request:
        :param args:
        :param kwargs:
        :return: super
        """
        if cache.get('filter_page'):
            self.success_url = cache.get('filter_page')

        return super().post(request, *args, **kwargs)


class FilterDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = Filter
    success_url = reverse_lazy('filter_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)


class GeolocationTaskCreate(CustomLoginRequiredView, View):

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        checkpointtype = request.POST.get('checkpointtype')
        task_id = request.POST.get('task_id')
        check_date = timezone.now()
        task = Task.objects.filter(pk=task_id).first()
        if task and latitude and longitude:
            taskgeolocation = TaskGeolocation.objects.filter(task=task, checkpointtype=checkpointtype).first()
            if taskgeolocation:
                taskgeolocation.latitude = Decimal(latitude)
                taskgeolocation.longitude = Decimal(longitude)
                taskgeolocation.date = check_date
                taskgeolocation.alter_user = request.user
                taskgeolocation.save()
            else:
                TaskGeolocation.objects.create(latitude=Decimal(latitude),
                                               longitude=Decimal(longitude),
                                               create_user=request.user,
                                               date=check_date,
                                               checkpointtype=checkpointtype,
                                               task=task
                                               )
            return JsonResponse({"ok": True,
                                 "latitude": latitude,
                                 "longitude": longitude,
                                 "check_date": date_format(timezone.localtime(check_date), 'DATETIME_FORMAT')})
        return JsonResponse({"ok": False})


class GeolocationTaskFinish(CustomLoginRequiredView, View):

    def post(self, request):
        finished_date = timezone.now()
        task_id = request.POST.get('task_id')
        task = Task.objects.filter(pk=task_id).first()
        if task:
            taskgeolocation = TaskGeolocation.objects.filter(task=task).first()
            if taskgeolocation:
                taskgeolocation.finished_date = finished_date
                taskgeolocation.alter_user = request.user
                taskgeolocation.save()
            return JsonResponse({"ok": True,
                                 "finished_date": date_format(timezone.localtime(finished_date), 'DATETIME_FORMAT')})
        return JsonResponse({"ok": False})
