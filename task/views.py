import json
import csv
import os
import copy
import pickle
import io
from urllib.parse import urlparse
from zipfile import ZipFile
from pathlib import Path
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import CustomLoginRequiredView
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db import IntegrityError, OperationalError
from django.db.models import Q, Case, When, CharField, IntegerField, Count
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django.core.exceptions import ValidationError
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin
from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, \
    operational_error_create, ioerror_create, exception_create, \
    integrity_error_delete, \
    DELETE_EXCEPTION_MESSAGE, success_sent, success_delete, NO_PERMISSIONS_DEFINED, record_from_wrong_office
from core.models import Person, Team
from core.views import AuditFormMixin, MultiDeleteViewMixin, SingleTableViewMixin
from etl.models import InconsistencyETL
from etl.tables import DashboardErrorStatusTable
from lawsuit.models import Movement, CourtDistrict
from task.filters import TaskFilter, TaskToPayFilter, TaskToReceiveFilter, OFFICE
from task.forms import TaskForm, TaskDetailForm, TaskCreateForm, TaskToAssignForm, FilterForm
from task.models import Task, TaskStatus, Ecm, TypeTask, TaskHistory, DashboardViewModel, Filter, TaskFeedback, \
    TaskGeolocation
from task.signals import send_notes_execution_date
from task.tables import TaskTable, DashboardStatusTable, FilterTable
from task.rules import RuleViewTask
from task.workflow import get_child_recipients
from financial.models import ServicePriceTable
from financial.tables import ServicePriceTableTaskTable
from core.utils import get_office_session, get_domain
from task.utils import get_task_attachment, copy_ecm
from decimal import Decimal
from guardian.core import ObjectPermissionChecker
from django.core.files.base import ContentFile
from functools import reduce
import operator

mapOrder = {
    'asc': '',
    'desc': '-'
}


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

    def post(selfTaskReportBase, request, *args, **kwargs):
        self.success_url = urlparse(request.META.get('HTTP_REFERER')).path
        return super(TaskDeleteView, self).post(request, *args, **kwargs)


class TaskReportBase(PermissionRequiredMixin, CustomLoginRequiredView, TemplateView):
    permission_required = ('core.view_all_tasks',)
    template_name = None
    filter_class = None
    datetime_field = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.task_filter = self.filter_class(data=self.request.GET, request=self.request)
        context['filter'] = self.task_filter
        try:
            if self.request.GET['group_by_tasks'] == OFFICE:
                office_list, total =  self.get_os_grouped_by_office()
            else:
                office_list, total =  self.get_os_grouped_by_client()
        except:
            office_list, total = self.get_os_grouped_by_office()
        context['offices'] = office_list
        context['total'] = total
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
                query.add(
                    Q(movement__law_suit__folder__person_customer__legal_name__unaccent__icontains=data['client']),
                    Q.AND)

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
        total = 0
        for task in tasks:
            correspondent = self._get_related_office(task)
            if correspondent not in offices_map:
                offices_map[correspondent] = {}
            client = self._get_related_client(task)
            if client not in offices_map[correspondent]:
                offices_map[correspondent][client] = []
            offices_map[correspondent][client].append(task)

        offices_map_total = {}
        for office, clients in offices_map.items():
            office_total = 0
            for client, tasks in clients.items():
                client_total = sum(map(lambda x: x.amount, tasks))
                office_total = office_total + client_total
                offices.append({
                    'office_name': office.name,
                    'client_name': client.name,
                    'tasks': tasks,
                    "client_total": client_total,
                    "office_total": 0,
                })
            offices_map_total[office.name] = office_total
            total = total + office_total

        for item in offices:
            item['office_total'] = offices_map_total[item['office_name']]

        return offices, total

    def get_os_grouped_by_client(self):
        clients = []
        clients_map = {}
        tasks = self.get_queryset()
        total = 0
        for task in tasks:
            client = self._get_related_client(task)
            if client not in clients_map:
                clients_map[client] = {}
            correspondent = self._get_related_office(task)
            if correspondent not in clients_map[client]:
                clients_map[client][correspondent] = []
            clients_map[client][correspondent].append(task)

        clients_map_total = {}
        for client, offices in clients_map.items():
            client_total = 0
            for office, tasks in offices.items():
                office_total = sum(map(lambda x: x.amount, tasks))
                client_total = client_total + office_total
                # necessário manter a mesma estrutura do get_os_grouped_by_office para não mexer no template.
                clients.append({
                    'office_name': client.name,
                    'client_name': office.name,
                    'tasks': tasks,
                    "client_total": office_total,
                    "office_total": 0,
                })
            clients_map_total[client.name] = client_total
            total = total + client_total

        for item in clients:
            item['office_total'] = clients_map_total[item['office_name']]

        return clients, total

    def _get_related_client(self, task):
        return task.client

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
    count_tasks_with_error = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        person = Person.objects.get(auth_user=self.request.user)
        context['task_count'] = self.count_task
        context['count_tasks_with_error'] = self.count_tasks_with_error

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
        self.count_task = len(data)
        self.count_tasks_with_error = len(data_error)

    def get_data(self, person):
        checker = ObjectPermissionChecker(person.auth_user)
        rule_view = RuleViewTask(request=self.request)
        dynamic_query = rule_view.get_dynamic_query(person, checker)
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
            if office_session.use_etl:
                return_list.append(DashboardErrorStatusTable(error,
                                                             title='Erro no sistema de origem',
                                                             status=TaskStatus.ERROR))

            # status 10 - Solicitada
            return_list.append(DashboardStatusTable(requested,
                                                    title='Solicitadas',
                                                    status=TaskStatus.REQUESTED))
            if office_session.use_service:
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
        offices_related = self.object.office.offices.all()
        context['correspondents_table'] = ServicePriceTableTaskTable(
            ServicePriceTable.objects.filter(Q(office=self.object.office) | Q(office__public_office=True),
                                             Q(Q(type_task=type_task) | Q(type_task=None)),
                                             Q(is_active=True),
                                             Q(office_correspondent__in=offices_related),
                                             Q(office_correspondent__is_active=True),
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
        if object_parent.get_child:
            if TaskStatus(object_parent.get_child.task_status) not in [TaskStatus.REFUSED, TaskStatus.REFUSED_SERVICE,
                                                                       TaskStatus.FINISHED]:
                return False
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
            new_ecm = copy_ecm(ecm, new_task)

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
    try:
        ecm = Ecm.objects.get(id=pk)
        task_id = ecm.task.pk
        ecm.delete()
        num_ged = Ecm.objects.filter(task_id=task_id).count()
        data = {'is_deleted': True,
                'num_ged': num_ged,
                'message': success_delete()
                }
    except IntegrityError:
        data = {'is_deleted': False,
                'num_ged': 1,
                'message': integrity_error_delete()
                }
    except Ecm.DoesNotExist:
        data = {'is_deleted': False,
                'num_ged': 1,
                'message': "Anexo já foi excluído ou não existe.",
                }
    except ValidationError as error:
        data = {'is_deleted': False,
                'num_ged': 1,
                'message': error.args[0],
                }
    except Exception as ex:
        data = {'is_deleted': False,
                'num_ged': 1,
                'message': DELETE_EXCEPTION_MESSAGE + '\n' + ex.args[0],
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
                team_dynamic_query = Q()

                if not checker.has_perm('can_distribute_tasks', office_session):
                    if checker.has_perm('view_delegated_tasks', office_session):
                        person_dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
                    if checker.has_perm('view_requested_tasks', office_session):
                        person_dynamic_query.add(Q(person_asked_by=person.id), Q.AND)
                if data['office_executed_by']:
                    task_dynamic_query.add(Q(child__office_id=data['office_executed_by']), Q.AND)
                if data['state']:
                    task_dynamic_query.add(Q(movement__law_suit__court_district__state=data['state']), Q.AND)
                if data['court_district']:
                    task_dynamic_query.add(Q(movement__law_suit__court_district=data['court_district']), Q.AND)
                if data['task_status']:
                    status = [getattr(TaskStatus, s) for s in data['task_status']]
                    task_dynamic_query.add(Q(task_status__in=status), Q.AND)
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
                    task_dynamic_query.add(Q(Q(legacy_code=data['task_origin_code'])
                                             | Q(parent_task_number=data['task_origin_code'])), Q.AND)
                if data['person_executed_by']:
                    task_dynamic_query.add(Q(person_executed_by=data['person_executed_by']), Q.AND)
                if data['person_asked_by']:
                    task_dynamic_query.add(Q(person_asked_by=data['person_asked_by']), Q.AND)
                if data['person_distributed_by']:
                    task_dynamic_query.add(Q(person_distributed_by=data['person_distributed_by']), Q.AND)
                if data['team']:
                    rule_view = RuleViewTask(self.request)
                    team_dynamic_query.add(rule_view.get_query_team_tasks([data['team']]), Q.AND)
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
                if data['final_deadline_date_in']:
                    if data['final_deadline_date_in'].start:
                        finished_dynamic_query.add(
                            Q(final_deadline_date__gte=data['final_deadline_date_in'].start.replace(hour=0, minute=0)), Q.AND)
                    if data['final_deadline_date_in'].stop:
                        finished_dynamic_query.add(
                            Q(final_deadline_date__lte=data['final_deadline_date_in'].stop.replace(hour=23, minute=59)), Q.AND)

                person_dynamic_query.add(Q(client_query), Q.AND) \
                    .add(Q(task_dynamic_query), Q.AND) \
                    .add(Q(team_dynamic_query), Q.AND) \
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

    def get(self, request, *args, **kwargs):
        checker = ObjectPermissionChecker(request.user)
        rule_view = RuleViewTask(request=request)
        dynamic_query = rule_view.get_dynamic_query(request.user.person, checker)
        status_totals = Task.objects.filter(dynamic_query).filter(is_active=True, office=get_office_session(request)).values('task_status').annotate(
            total=Count('task_status')).order_by('task_status')
        ret = {}
        total = 0
        for status in status_totals:
            ret[status['task_status'].replace(' ', '_').lower()] = status['total']
            total += status['total']
        ret['total'] = total
        return JsonResponse(ret)


@login_required
def ajax_get_task_data_table(request):
    status = request.GET.get('status')
    data_dict = json.loads(request.GET.get('data', '{}'))
    draw = int(data_dict.get('draw', 0))
    start = int(data_dict.get('start', 0))
    length = int(data_dict.get('length', 5))
    search_dict = data_dict.get('search', {})
    columns = data_dict.get('columns', [])
    order_dict = data_dict.get('order', {})
    checker = ObjectPermissionChecker(request.user)
    dash = DashboardView()
    dash.request = request
    rule_view = RuleViewTask(request=request)
    dynamic_query = rule_view.get_dynamic_query(request.user.person, checker)
    values_list = ['pk', 'task_number', 'final_deadline_date', 'type_task__name', 'movement__law_suit__law_suit_number',
                   'movement__law_suit__court_district__name', 'movement__law_suit__court_district__state__initials',
                   'movement__law_suit__folder__person_customer__legal_name', 'movement__law_suit__opposing_party',
                   'delegation_date', 'task_original']
    if status == 'Erro no sistema de origem':
        values_list.extend(['inconsistencyetl__inconsistency', 'inconsistencyetl__solution'])
    query = Task.objects.filter(dynamic_query).filter(is_active=True, task_status=status,
                                                      office=get_office_session(request)).select_related(
        'type_task', 'movement__law_suit', 'movement__law_suit__court_district',
        'movement__law_suit__court_district__state', 'movement__law_suit__folder__person_customer', 'parent'
    ).annotate(
        task_original=Case(
            When(parent_id__isnull=False, then=Cast('parent__task_number', CharField(max_length=255))),
            default=Cast('legacy_code', CharField(max_length=255)),
            output_field=CharField(max_length=255),
        ),
    ).values(*values_list)


    # criando o filtro de busca a partir do valor enviado no campo de pesquisa
    search_value = search_dict.get('value', None)
    reduced_filter = None
    if search_value:
        search_dict_query = {}
        for column in columns:
            if column.get('searchable'):
                key = '{}__icontains'.format(column.get('data'))
                search_dict_query[key] = search_value
        reduced_filter = reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in search_dict_query.items()]))

    #criando lista de ordered
    ordered_list = list(map(lambda i: '{}{}'.format(mapOrder.get(i.get('dir')), i.get('column')), order_dict))


    records_total = query.count()
    if not ordered_list:
        ordered_list = ['final_deadline_date']
    if reduced_filter:
        query = query.filter(reduced_filter).order_by(*ordered_list)
    else:
        query = query.order_by(*ordered_list)

    records_filtered = query.count()
    xdata = [x for x in query[start:start + length]]
    data = {
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": xdata
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

@login_required
def ecm_batch_download(request, pk):
    #https://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable
    #http://mypythondjango.blogspot.com/2018/01/how-to-zip-files-in-filefield-and.html
    ecms = Ecm.objects.filter(task_id=pk).select_related('task')
    try:
        buff = io.BytesIO()
        zf = ZipFile(buff, mode='a')
        zip_filename = None
        for ecm in ecms:
            output = io.BytesIO(ecm.path.read())
            output.seek(0)
            zf.writestr(ecm.path.name, output.getvalue())
            if not zip_filename:
                zip_filename = 'Anexos_OS_%s.zip' % (ecm.task.task_number)
        zf.close()
        buff.seek(0)
        data = buff.read()
        resp = HttpResponse(data, content_type = "application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    except Exception as e:
        messages.error(request, 'Erro ao baixar todos arquivos.' + str(e))
        return HttpResponseRedirect(ecm.task.get_absolute_url())