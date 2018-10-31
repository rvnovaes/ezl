import json
import uuid
import csv
import copy
import pickle
import io
from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import CustomLoginRequiredView, set_office_session
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db import IntegrityError, OperationalError
from django.db.models import Q, Case, When, CharField, IntegerField, Count
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.forms.models import model_to_dict
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin
from djmoney.money import Money
from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, \
    operational_error_create, ioerror_create, exception_create, \
    integrity_error_delete, \
    DELETE_EXCEPTION_MESSAGE, success_sent, success_delete, NO_PERMISSIONS_DEFINED, record_from_wrong_office
from core.models import Person, CorePermissions, CustomSettings
from core.views import AuditFormMixin, MultiDeleteViewMixin, SingleTableViewMixin
from lawsuit.models import Movement
from task.filters import TaskFilter, TaskToPayFilter, TaskToReceiveFilter, OFFICE, BatchChangTaskFilter
from task.forms import TaskForm, TaskDetailForm, TaskCreateForm, TaskToAssignForm, FilterForm, TypeTaskForm, ImportTaskListForm, TaskSurveyAnswerForm
from task.models import Task, Ecm, TaskStatus, TypeTask, TaskHistory, DashboardViewModel, Filter, TaskFeedback, \
    TaskGeolocation, TypeTaskMain, TaskSurveyAnswer
from task.signals import send_notes_execution_date
from task.tables import TaskTable, DashboardStatusTable, FilterTable, TypeTaskTable
from task.tasks import import_xls_task_list
from task.rules import RuleViewTask
from task.workflow import CorrespondentsTable
from task.workflow import get_child_recipients
from financial.models import ServicePriceTable
from core.utils import get_office_session, get_domain
from task.utils import get_task_attachment, clone_task_ecms, get_dashboard_tasks, get_task_ecms, delegate_child_task
from decimal import Decimal
from guardian.core import ObjectPermissionChecker
from functools import reduce
import operator
from django.shortcuts import render
import os
from django.conf import settings
from urllib.parse import urljoin


import logging
logger = logging.getLogger(__name__)

mapOrder = {'asc': '', 'desc': '-'}


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

        documents = self.request.FILES.getlist('file')
        if documents:
            for document in documents:
                file_name = document.name.replace(' ', '_')
                task.ecm_set.create(
                    path=document,
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
            lawsuit_id = Movement.objects.get(
                id=self.kwargs.get('movement')).law_suit_id
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

        documents = self.request.FILES.getlist('file')
        if documents:
            for document in documents:
                file_name = document.name.replace(' ', '_')
                task.ecm_set.create(
                    path=document,
                    exhibition_name=file_name,
                    create_user=task.create_user)

        form.delete_temporary_files()

        return response

    def get_success_url(self):
        return reverse(
            'movement_update',
            kwargs={
                'lawsuit': self.kwargs['lawsuit'],
                'pk': self.kwargs['movement']
            })


class TaskToAssignView(AuditFormMixin, UpdateView):
    model = Task
    form_class = TaskToAssignForm
    success_url = reverse_lazy('dashboard')
    template_name_suffix = '_to_assign'

    def save_form(self, form):
        if form.is_valid():
            form.instance.person_distributed_by = self.request.user.person
            form.instance.task_status = TaskStatus.OPEN
            # TODO: rever processo de anexo, quando for trocar para o ECM Generico
            get_task_attachment(self, form)
            form.save()

    def form_valid(self, form):
        super().form_valid(form)
        self.save_form(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def form_invalid(self, form):
        super().form_invalid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))


class BatchTaskToAssignView(AuditFormMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        try:
            task_id = kwargs.get('pk')
            task = Task.objects.get(pk=task_id)
            form = TaskToAssignForm(request.POST, instance=task)
            if form.is_valid():
                form.instance.person_executed_by_id = request.POST.get('person_executed_by')
                form.instance.person_distributed_by = self.request.user.person
                form.instance.task_status = TaskStatus.OPEN
                get_task_attachment(self, form)
                form.save()
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'errors': form})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class BatchTaskToDelegateView(AuditFormMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(pk=kwargs.get('pk'))
            amount = request.POST.get('amount').replace('R$', '') if request.POST.get('amount') else '0.00'
            note = request.POST.get('note', '')
            form = TaskDetailForm(request.POST, instance=task)
            if form.is_valid():
                form.instance.task_status = TaskStatus.OPEN
                form.instance.amount = Decimal(amount)
                get_task_attachment(self, form)
                form.instance.delegation_date = timezone.now()
                if not form.instance.person_distributed_by:
                    form.instance.person_distributed_by = request.user.person
                servicepricetable = ServicePriceTable.objects.get(
                    pk=request.POST.get('servicepricetable_id'))
                if servicepricetable:
                    delegate_child_task(form.instance, servicepricetable.office_correspondent)
                    form.instance.person_executed_by = None
                send_notes_execution_date.send(
                    sender=self.__class__,
                    notes=note,
                    instance=form.instance,
                    execution_date=form.instance.execution_date,
                    survey_result=form.instance.survey_result)
                form.save()
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'errors': form})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class BatchTaskToRefuseView(AuditFormMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        task = Task.objects.get(pk=kwargs.get('pk'))
        task.task_status = TaskStatus.REFUSED
        send_notes_execution_date.send(
            sender=self.__class__,
            notes=request.POST.get('notes'),
            instance=task,
            execution_date=task.execution_date,
            survey_result=task.survey_result)
        task.save()
        return JsonResponse({'status': 'ok'})


class TaskUpdateView(AuditFormMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_persist_form'

    def get_initial(self):
        if self.kwargs.get('movement'):
            lawsuit_id = Movement.objects.get(
                id=self.kwargs.get('movement')).law_suit_id
            self.kwargs['lawsuit'] = lawsuit_id
            self.success_url = reverse(
                'movement_update',
                kwargs={
                    'lawsuit': self.kwargs['lawsuit'],
                    'pk': self.kwargs['movement']
                })
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
                task.ecm_set.create(
                    path=document,
                    exhibition_name=file_name,
                    create_user=task.create_user)

        form.delete_temporary_files()
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)

        return context


class TaskDeleteView(SuccessMessageMixin, CustomLoginRequiredView,
                     MultiDeleteViewMixin):
    model = Task
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)

    def post(self, request, *args, **kwargs):
        self.success_url = urlparse(request.META.get('HTTP_REFERER')).path
        return super(TaskDeleteView, self).post(request, *args, **kwargs)


class TaskReportBase(PermissionRequiredMixin, CustomLoginRequiredView,
                     TemplateView):
    permission_required = ('core.view_all_tasks', )
    template_name = None
    filter_class = None
    datetime_field = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.task_filter = self.filter_class(
            data=self.request.GET, request=self.request)
        context['filter'] = self.task_filter
        try:
            if self.request.GET['group_by_tasks'] == OFFICE:
                office_list, total = self.get_os_grouped_by_office()
            else:
                office_list, total = self.get_os_grouped_by_client()
        except:
            office_list, total = self.get_os_grouped_by_office()
        context['offices_report'] = office_list
        context['total'] = total
        return context

    def get_queryset(self):
        office = get_office_session(self.request)
        queryset = Task.objects.filter(
            office=office,
            task_status=TaskStatus.FINISHED,
            child__isnull=False)
        queryset = self.filter_queryset(queryset)
        return queryset.order_by('child__office__name')

    def filter_queryset(self, queryset):
        if not self.task_filter.form.is_valid():
            messages.add_message(self.request, messages.ERROR,
                                 'Formulário inválido.')
        else:
            data = self.task_filter.form.cleaned_data
            query = Q()
            finished_query = Q()

            if data['status']:
                key = "{}__isnull".format(self.datetime_field)
                query.add(Q(**{key: data['status'] != 'true'}), Q.AND)

            if data['client']:
                query.add(
                    Q(movement__law_suit__folder__person_customer__legal_name__unaccent__icontains
                      =data['client']), Q.AND)

            if data['office']:
                if isinstance(self, ToReceiveTaskReportView):
                    query.add(
                        Q(parent__office__name__unaccent__icontains=data[
                            'office']), Q.AND)
                else:
                    query.add(
                        Q(office__name__unaccent__icontains=data['office']),
                        Q.AND)

            if data['finished_in']:
                if data['finished_in'].start:
                    finished_query.add(
                        Q(finished_date__gte=data['finished_in'].start.replace(
                            hour=0, minute=0)), Q.AND)
                if data['finished_in'].stop:
                    finished_query.add(
                        Q(finished_date__lte=data['finished_in'].stop.replace(
                            hour=23, minute=59)), Q.AND)

            if 'refunds_correspondent_service' in data and data['refunds_correspondent_service']:
                refunds = (data['refunds_correspondent_service'] == 'True')
                query.add(
                    Q(movement__law_suit__folder__person_customer__refunds_correspondent_service=refunds),
                    Q.AND)

            if query or finished_query:
                query.add(Q(finished_query), Q.AND)
                queryset = queryset.filter(query)
            else:
                queryset = Task.objects.none()

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
                    'client_refunds': client.refunds_correspondent_service,
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
            parent__isnull=False)
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

        messages.add_message(self.request, messages.INFO,
                             "OS's marcadas como recebidas com sucesso.")
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
            parent__isnull=False)
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

        messages.add_message(self.request, messages.INFO,
                             "OS's faturadas com sucesso.")
        return JsonResponse({"status": "ok"})


class DashboardView(CustomLoginRequiredView, TemplateView):
    template_name = 'task/task_dashboard.html'
    table_pagination = {'per_page': 5}
    ret_status_dict = {}

    def get(self, request, *args, **kwargs):
        office_session = get_office_session(request)
        checker = ObjectPermissionChecker(request.user)
        company_representative = checker.has_perm('can_see_tasks_company_representative', office_session)
        view_all_tasks = checker.has_perm('view_all_tasks', office_session)
        if company_representative and not view_all_tasks:
            return HttpResponseRedirect(reverse_lazy('task_to_company_representative'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        office_session = get_office_session(self.request)
        context = super().get_context_data(*args, **kwargs)
        custom_settings = CustomSettings.objects.filter(
            office=office_session).first()
        context['cards_to_show'] = []
        if custom_settings and custom_settings.task_status_show:
            context['cards_to_show'] = list(
                custom_settings.task_status_show.values_list(
                    'status_to_show', flat=True))
        person = Person.objects.get(auth_user=self.request.user)
        checker = ObjectPermissionChecker(person.auth_user)
        ret_status_dict, office_session = self.get_data(person, checker)
        context['ret_status_dict'] = ret_status_dict

        if not self.request.user.get_all_permissions():
            context['messages'] = [{
                'tags': 'error',
                'message': NO_PERMISSIONS_DEFINED
            }]
        return context

    def get_data(self, person, checker):
        office_session = get_office_session(self.request)
        data, exclude_status = get_dashboard_tasks(
            self.request, office_session, checker, person)
        ret_status_dict = self.get_ret_status_dict(data, exclude_status)

        return ret_status_dict, office_session

    @staticmethod
    def get_ret_status_dict(data, exclude_status):
        status_totals = data.values('task_status').annotate(
            total=Count('task_status')).order_by('task_status')
        total = 0
        status_dict = {}
        for task_status in TaskStatus:
            if task_status.value not in exclude_status:
                status = status_totals.filter(task_status=task_status).first()
                task_status_value = task_status.value
                task_status_total = status['total'] if status else 0
                status_dict[task_status.get_status_order] = {
                    'status': task_status_value,
                    'total': task_status_total,
                    'name': task_status.name,
                    'title': task_status_value,
                    'task_icon': task_status.get_icon
                }
                total += task_status_total

        ret_status_dict = {}
        for status_key in sorted(status_dict.keys()):
            ret_status_dict[str(status_key)] = status_dict[status_key]
        ret_status_dict['total'] = total
        ret_status_dict['total_requested_month'] = data.filter(
            requested_date__year=datetime.today().year,
            requested_date__month=datetime.today().month).count()

        return ret_status_dict


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
        form.instance.task_status = TaskStatus[
            self.request.POST['action']] or TaskStatus.INVALID
        form.instance.alter_user = User.objects.get(id=self.request.user.id)
        notes = form.cleaned_data['notes'] if form.cleaned_data[
            'notes'] else None
        execution_date = (form.cleaned_data['execution_date']
                          if form.cleaned_data['execution_date'] else
                          form.initial['execution_date'])
        survey_result = (form.cleaned_data['survey_result']
                         if form.cleaned_data['survey_result'] else
                         form.initial['survey_result'])
        if survey_result:
            survey = TaskSurveyAnswer()
            survey.task = form.instance
            survey.create_user = self.request.user
            survey.survey_result = survey_result
            survey.save()
        send_notes_execution_date.send(
            sender=self.__class__,
            notes=notes,
            instance=form.instance,
            execution_date=execution_date,
            survey_result=survey_result,
            **{'external_task': True})
        form.instance.__server = get_domain(self.request)
        if form.instance.task_status == TaskStatus.ACCEPTED_SERVICE:
            form.instance.person_distributed_by = self.request.user.person
        if form.instance.task_status == TaskStatus.REFUSED_SERVICE:
            form.instance.person_distributed_by = self.request.user.person
        if form.instance.task_status == TaskStatus.REFUSED and not form.instance.person_distributed_by:
            form.instance.person_distributed_by = self.request.user.person
        if form.instance.task_status == TaskStatus.OPEN:
            form.instance.delegation_date = timezone.now()
            if not form.instance.person_distributed_by:
                form.instance.person_distributed_by = self.request.user.person
            default_amount = Decimal(
                '0.00') if not form.instance.amount else form.instance.amount
            form.instance.amount = (form.cleaned_data['amount']
                                    if form.cleaned_data['amount'] else
                                    default_amount)
            servicepricetable_id = (
                self.request.POST['servicepricetable_id']
                if self.request.POST['servicepricetable_id'] else None)
            servicepricetable = ServicePriceTable.objects.filter(
                id=servicepricetable_id).first()
            get_task_attachment(self, form)
            if servicepricetable:
                delegate_child_task(
                    form.instance, servicepricetable.office_correspondent)
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
        office_session = get_office_session(self.request)
        custom_settings = CustomSettings.objects.filter(
            office=office_session).first()
        context['custom_settings'] = custom_settings
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)
        context['task_history'] = \
            TaskHistory.objects.filter(
                task_id=self.object.id).order_by('-create_date')
        context['survey_data'] = (self.object.type_task.survey.data
                                  if self.object.type_task.survey else None)
        if self.object.parent:
            context['survey_data'] = (self.object.parent.type_task.survey.data
                                      if self.object.parent.type_task.survey
                                      else None)
        office_session = get_office_session(self.request)
        get_correspondents_table = CorrespondentsTable(self.object,
                                                       office_session)
        context[
            'correspondents_table'] = get_correspondents_table.get_correspondents_table(
            )
        type_task_field = get_correspondents_table.get_type_task_field()
        if type_task_field:
            context['form'].fields['type_task_field'] = type_task_field
        checker = ObjectPermissionChecker(self.request.user)        
        if checker.has_perm('can_see_tasks_company_representative', office_session):            
            if not TaskSurveyAnswer.objects.filter(task=self.object, create_user=self.request.user):
                if (self.object.type_task.survey):
                    context['not_answer_questionnarie'] = True
                    context['survey_company_representative'] = self.object.type_task.survey.data
        return context



    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        office_session = get_office_session(request)
        if office_session != Task.objects.filter(
                pk=kwargs.get('pk')).first().office:
            messages.error(
                self.request,
                "A OS que está tentando acessar, não pertence ao escritório selecionado."
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
        data = {'success': False, 'message': exception_create()}
        for file in files:
            file_name = file._name.replace(' ', '_')
            obj_task = Task.objects.get(id=task)
            ecm = Ecm(
                path=file,
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
                data = {
                    'success': False,
                    'message': operational_error_create()
                }
            except IOError:
                data = {'is_deleted': False, 'message': ioerror_create()}
            except Exception:
                data = {'success': False, 'message': exception_create()}

        return JsonResponse(data)


def delete_ecm(request, pk):
    try:
        ecm = Ecm.objects.get(id=pk)
        task_id = ecm.task.pk
        ecm.delete()
        num_ged = Ecm.objects.filter(task_id=task_id).count()
        data = {
            'is_deleted': True,
            'num_ged': num_ged,
            'message': success_delete()
        }
    except IntegrityError:
        data = {
            'is_deleted': False,
            'num_ged': 1,
            'message': integrity_error_delete()
        }
    except Ecm.DoesNotExist:
        data = {
            'is_deleted': False,
            'num_ged': 1,
            'message': "Anexo já foi excluído ou não existe.",
        }
    except ValidationError as error:
        data = {
            'is_deleted': False,
            'num_ged': 1,
            'message': error.args[0],
        }
    except Exception as ex:
        data = {
            'is_deleted': False,
            'num_ged': 1,
            'message': DELETE_EXCEPTION_MESSAGE + '\n' + ex.args[0],
        }

    return JsonResponse(data)


@login_required
def delete_internal_ecm(request, pk):
    return delete_ecm(request, pk)


def delete_external_ecm(request, task_hash, pk):
    # Para usuario que apenas acessam a task por hash, sem autenticar
    task = Task.objects.get(task_hash=task_hash)
    ecm = Ecm.objects.get(pk=pk)
    if ecm.task.task_hash.hex == task_hash:
        return delete_ecm(request, pk)
    return JsonResponse({'message': 'Hash inválido'})


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
        task_filter = self.filter_class(data=filters, request=self.request)
        task_form = task_filter.form

        if task_form.is_valid():
            data = task_form.cleaned_data
            import logging
            logger = logging.getLogger('teste')
            logger.info(data)


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

                if not checker.has_perm('can_distribute_tasks',
                                        office_session):
                    if checker.has_perm('view_delegated_tasks',
                                        office_session):
                        person_dynamic_query.add(
                            Q(person_executed_by=person.id), Q.OR)
                    if checker.has_perm('view_requested_tasks',
                                        office_session):
                        person_dynamic_query.add(
                            Q(person_asked_by=person.id), Q.OR)
                if data['office_executed_by']:
                    task_dynamic_query.add(
                        Q(child__office_id=data['office_executed_by']), Q.AND)
                if data['state']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__court_district__state=data[
                            'state']), Q.AND)
                if data['court_district']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__court_district=data[
                            'court_district']), Q.AND)
                if data['court_district_complement']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__court_district_complement=data[
                            'court_district_complement']), Q.AND)
                if data.get('task_status'):
                    status = [
                        getattr(TaskStatus, s) for s in data['task_status']
                    ]
                    task_dynamic_query.add(Q(task_status__in=status), Q.AND)
                if data['type_task']:
                    task_dynamic_query.add(
                        Q(Q(type_task=data['type_task']) |
                          Q(type_task__type_task_main__in=data['type_task'].type_task_main.all())), Q.AND)
                if data['court']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__organ=data['court']), Q.AND)
                if data['cost_center']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__folder__cost_center=data[
                            'cost_center']), Q.AND)
                if data['folder_number']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__folder__folder_number=data[
                            'folder_number']), Q.AND)
                if data['folder_legacy_code']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__folder__legacy_code=data[
                            'folder_legacy_code']), Q.AND)
                if data['client']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__folder__person_customer__id=data[
                            'client']), Q.AND)
                if data['law_suit_number']:
                    task_dynamic_query.add(
                        Q(movement__law_suit__law_suit_number=data[
                            'law_suit_number']), Q.AND)
                if data['task_number']:
                    task_dynamic_query.add(
                        Q(task_number=data['task_number']), Q.AND)
                if data['task_origin_code']:
                    task_dynamic_query.add(
                        Q(
                            Q(legacy_code=data['task_origin_code'])
                            | Q(parent_task_number=data['task_origin_code'])),
                        Q.AND)
                if data['person_executed_by']:
                    task_dynamic_query.add(
                        Q(person_executed_by=data['person_executed_by']),
                        Q.AND)
                if data['person_asked_by']:
                    task_dynamic_query.add(
                        Q(person_asked_by=data['person_asked_by']), Q.AND)
                if data['origin_office_asked_by']:
                    task_dynamic_query.add(
                        Q(office=office_session, parent__office_id=data['origin_office_asked_by']), Q.AND)
                if data['person_distributed_by']:
                    task_dynamic_query.add(
                        Q(person_distributed_by=data['person_distributed_by']),
                        Q.AND)
                if data['team']:
                    rule_view = RuleViewTask(self.request)
                    team_dynamic_query.add(
                        rule_view.get_query_team_tasks([data['team']]), Q.AND)
                if data['requested_in']:
                    if data['requested_in'].start:
                        requested_dynamic_query.add(
                            Q(requested_date__gte=data['requested_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['requested_in'].stop:
                        requested_dynamic_query.add(
                            Q(requested_date__lte=data['requested_in'].stop.
                              replace(hour=23, minute=59)), Q.AND)
                if data['accepted_service_in']:
                    if data['accepted_service_in'].start:
                        accepted_service_dynamic_query.add(
                            Q(acceptance_service_date__gte=data[
                                'accepted_service_in'].start.replace(
                                    hour=0, minute=0)), Q.AND)
                    if data['accepted_service_in'].stop:
                        accepted_service_dynamic_query.add(
                            Q(acceptance_service_date__lte=data[
                                'accepted_service_in'].stop.replace(
                                    hour=23, minute=59)), Q.AND)
                if data['refused_service_in']:
                    if data['refused_service_in'].start:
                        refused_service_query.add(
                            Q(refused_service_date__gte=data[
                                'refused_service_in'].start.replace(
                                    hour=0, minute=0)), Q.AND)
                    if data['refused_service_in'].stop:
                        refused_service_query.add(
                            Q(refused_service_date__lte=data[
                                'refused_service_in'].stop.replace(
                                    hour=23, minute=59)), Q.AND)
                if data['open_in']:
                    if data['open_in'].start:
                        open_dynamic_query.add(
                            Q(delegation_date__gte=data['open_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['open_in'].stop:
                        open_dynamic_query.add(
                            Q(delegation_date__lte=data['open_in'].stop.
                              replace(hour=23, minute=59)), Q.AND)
                if data['accepted_in']:
                    if data['accepted_in'].start:
                        accepted_dynamic_query.add(
                            Q(acceptance_date__gte=data['accepted_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['accepted_in'].stop:
                        accepted_dynamic_query.add(
                            Q(acceptance_date__lte=data['accepted_in'].stop.
                              replace(hour=23, minute=59)), Q.AND)
                if data['refused_in']:
                    if data['refused_in'].start:
                        refused_dynamic_query.add(
                            Q(refused_date__gte=data['refused_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['refused_in'].stop:
                        refused_dynamic_query.add(
                            Q(refused_date__lte=data['refused_in'].stop.
                              replace(hour=23, minute=59)), Q.AND)
                if data['return_in']:
                    if data['return_in'].start:
                        return_dynamic_query.add(
                            Q(return_date__gte=data['return_in'].start.replace(
                                hour=0, minute=0)), Q.AND)
                    if data['return_in'].stop:
                        return_dynamic_query.add(
                            Q(return_date__lte=data['return_in'].stop.replace(
                                hour=23, minute=59)), Q.AND)
                if data['done_in']:
                    if data['done_in'].start:
                        done_dynamic_query.add(
                            Q(execution_date__gte=data['done_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['done_in'].stop:
                        done_dynamic_query.add(
                            Q(execution_date__lte=data['done_in'].stop.replace(
                                hour=23, minute=59)), Q.AND)
                if data['blocked_payment_in']:
                    if data['blocked_payment_in'].start:
                        blocked_payment_dynamic_query.add(
                            Q(blocked_payment_date__gte=data[
                                'blocked_payment_in'].start.replace(
                                    hour=0, minute=0)), Q.AND)
                    if data['blocked_payment_in'].stop:
                        blocked_payment_dynamic_query.add(
                            Q(blocked_payment_date__lte=data[
                                'blocked_payment_in'].stop.replace(
                                    hour=23, minute=59)), Q.AND)
                if data['finished_in']:
                    if data['finished_in'].start:
                        finished_dynamic_query.add(
                            Q(finished_date__gte=data['finished_in'].start.
                              replace(hour=0, minute=0)), Q.AND)
                    if data['finished_in'].stop:
                        finished_dynamic_query.add(
                            Q(finished_date__lte=data['finished_in'].stop.
                              replace(hour=23, minute=59)), Q.AND)
                if data['final_deadline_date_in']:
                    if data['final_deadline_date_in'].start:
                        finished_dynamic_query.add(
                            Q(final_deadline_date__gte=data[
                                'final_deadline_date_in'].start.replace(
                                    hour=0, minute=0)), Q.AND)
                    if data['final_deadline_date_in'].stop:
                        finished_dynamic_query.add(
                            Q(final_deadline_date__lte=data[
                                'final_deadline_date_in'].stop.replace(
                                    hour=23, minute=59)), Q.AND)

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

                office_id = (get_office_session(self.request).id
                             if get_office_session(self.request) else 0)
                query_set = DashboardViewModel.objects.filter(
                    office_id=office_id).filter(person_dynamic_query)

            try:
                if filters.get('save_filter', None) is not None:
                    filter_name = data['custom_filter_name']
                    filter_description = data['custom_filter_description']
                    q = pickle.dumps(person_dynamic_query)
                    new_filter = Filter(
                        name=filter_name,
                        query=q,
                        description=filter_description,
                        create_user=self.request.user,
                        create_date=timezone.now())
                    new_filter.save()
            except IntegrityError:
                messages.add_message(self.request, messages.ERROR,
                                     'Já existe filtro com este nome.')
        else:
            messages.add_message(self.request, messages.ERROR,
                                 'Formulário inválido.')
        return query_set, task_filter

    def get_queryset(self, **kwargs):

        task_list, task_filter = self.query_builder()
        self.filter = task_filter

        return task_list

    def get_context_data(self, **kwargs):
        context = super(DashboardSearchView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        table = self.table_class(self.object_list)
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get(self, request, *args, **kwargs):
        checker = ObjectPermissionChecker(self.request.user)
        if (self.request.GET.get('export_answers') and checker.has_perm(
                'can_view_survey_results', get_office_session(request))):
            return self._export_answers(request)

        return super().get(request)

    def _export_answers(self, request):
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename="respostas_dos_formularios.csv"'
        writer = csv.writer(response)

        queryset = self.get_queryset().filter(survey_result__isnull=False)
        tasks = self._fill_tasks_answers(queryset)
        columns = self._get_answers_columns(tasks)
        writer.writerow(['N° da OS', 'N° da OS no sistema de origem'] +
                        columns)

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
        office_session = get_office_session(request)
        data, exclude_status = get_dashboard_tasks(
            request, office_session, checker, request.user.person)

        status_totals = data.values('task_status').annotate(
            total=Count('task_status')).order_by('task_status')

        ret = {'office': office_session.legal_name}
        total = 0
        for status in status_totals:
            ret[status['task_status'].replace(' ',
                                              '_').lower()] = status['total']
            total += status['total']

        ret['total'] = total
        ret['total_requested_month'] = data.filter(
            requested_date__year=datetime.today().year,
            requested_date__month=datetime.today().month).count()

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
    values_list = [
        'pk', 'task_number', 'final_deadline_date', 'type_task__name',
        'movement__law_suit__law_suit_number',
        'movement__law_suit__court_district__name',
        'movement__law_suit__court_district__state__initials',
        'movement__law_suit__folder__person_customer__legal_name',
        'movement__law_suit__opposing_party', 'movement__law_suit__court_district_complement__name',
        'task_original'
    ]
    if status == 'Erro no sistema de origem':
        values_list.extend(
            ['inconsistencyetl__inconsistency', 'inconsistencyetl__solution'])
    query = Task.objects.filter(dynamic_query).filter(
        is_active=True, task_status=status,
        office=get_office_session(request)).select_related(
            'type_task', 'movement__law_suit',
            'movement__law_suit__court_district',
            'movement__law_suit__court_district__state',
            'movement__law_suit__folder__person_customer', 'movement__law_suit__court_district_complement__name', 'parent').annotate(
                task_original=Case(
                    When(
                        parent_id__isnull=False,
                        then=Cast('parent__task_number',
                                  CharField(max_length=255))),
                    default=Cast('legacy_code', CharField(max_length=255)),
                    output_field=CharField(max_length=255),
                ), ).values(*values_list)

    # criando o filtro de busca a partir do valor enviado no campo de pesquisa
    search_value = search_dict.get('value', None)
    reduced_filter = None
    if search_value:
        search_dict_query = {}
        for column in columns:
            if column.get('searchable'):
                key = '{}__icontains'.format(column.get('data'))
                search_dict_query[key] = search_value
        reduced_filter = reduce(
            operator.or_,
            (Q(**d) for d in [dict([i]) for i in search_dict_query.items()]))

    # criando lista de ordered
    ordered_list = list(map(lambda i: '{}{}'.format(
        mapOrder.get(i.get('dir')), i.get('column')), order_dict))

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


@login_required
def ajax_get_correspondents_table(request):
    type_task_id = request.GET.get('type_task', 0)
    task_id = request.GET.get('task', 0)
    correspondents_table_list = []
    type_task_name = None
    if type_task_id and task_id:
        type_task = TypeTask.objects.filter(pk=type_task_id).first()
        task = Task.objects.filter(pk=task_id).first()
        office = get_office_session(request)
        get_correspondents_table = CorrespondentsTable(
            task, office, type_task=type_task)
        type_task = get_correspondents_table.update_type_task(type_task)
        type_task_name = type_task.name
        type_task_id = type_task.id
        correspondents_table = get_correspondents_table.get_correspondents_table(
        )
        correspondents_table_list = list(map(lambda x: {
            'pk': x.pk,
            'office': x.office.legal_name,
            'office_correspondent': x.office_correspondent.legal_name,
            'court_district': x.court_district.name if x.court_district else '—',
            'state': x.state.name if x.state else '—',
            'client': x.client.legal_name if x.client else '—',
            'value': x.value,
            'formated_value': Money(x.value, 'BRL').__str__(),
            'office_rating': x.office_rating if x.office_rating else '0.00',
            'office_return_rating': x.office_return_rating if x.office_return_rating else '0.00',
            'office_public': x.office_correspondent.public_office
        }, correspondents_table.data.data))
    data = {
        "correspondents_table": correspondents_table_list,
        "type_task": type_task_name,
        "type_task_id": type_task_id,
        "total": correspondents_table_list.__len__()
    }
    return JsonResponse(data)


def get_ecm_url(ecm, external=False):
    if external: 
        return '{path}/{task_hash}/'.format(path=ecm.path.name, task_hash=ecm.task.task_hash.hex)
    return ecm.path.name


def get_ecms(task_id, external=False):
    data_list = []
    ecms = get_task_ecms(task_id)
    for ecm in ecms:
        data_list.append({
            'task_id': ecm.task_id,
            'pk': ecm.pk,
            'url': get_ecm_url(ecm, external=external),
            'base_external_url': '/providencias' if external else '',
            'filename': ecm.filename,
            'exhibition_name': ecm.exhibition_name if ecm.exhibition_name else ecm.filename,
            'user': ecm.create_user.username,
            'data': timezone.localtime(ecm.create_date).strftime('%d/%m/%Y %H:%M'),
            'state': ecm.task.get_task_status_display(),
        })
    data = {'task_id': task_id, 'total_ecms': ecms.count(), 'ecms': data_list}
    return JsonResponse(data)


def ajax_get_ecms(request):
    task_id = request.GET.get('task_id')
    return get_ecms(task_id)


def get_external_ecms(request):
    task = Task.objects.filter(task_hash=request.GET.get('task_hash')).first()
    return get_ecms(task.pk, external=True)


class ExternalMediaFileView(View):
    def get(self, request, path, task_hash):
        if Ecm.objects.filter(task__task_hash=task_hash, path=path).exists():            
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, path)):
                return static_serve_view(
                    self.request, path, document_root=settings.MEDIA_ROOT)
            return HttpResponseRedirect(
                urljoin(settings.AWS_STORAGE_BUCKET_URL, path))
        raise Http404('Arquivo não existe')
        

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
        if not checker.has_perm('group_admin', get_office_session(
                self.request)):
            context['table'] = self.table_class(
                context['table'].data.data.filter(
                    create_user=self.request.user))
        RequestConfig(
            self.request, paginate={
                'per_page': 10
            }).configure(context['table'])
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
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class GeolocationTaskCreate(CustomLoginRequiredView, View):
    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        checkpointtype = request.POST.get('checkpointtype')
        task_id = request.POST.get('task_id')
        check_date = timezone.now()
        task = Task.objects.filter(pk=task_id).first()
        if task and latitude and longitude:
            taskgeolocation = TaskGeolocation.objects.filter(
                task=task, checkpointtype=checkpointtype).first()
            if taskgeolocation:
                taskgeolocation.latitude = Decimal(latitude)
                taskgeolocation.longitude = Decimal(longitude)
                taskgeolocation.date = check_date
                taskgeolocation.alter_user = request.user
                taskgeolocation.save()
            else:
                TaskGeolocation.objects.create(
                    latitude=Decimal(latitude),
                    longitude=Decimal(longitude),
                    create_user=request.user,
                    date=check_date,
                    checkpointtype=checkpointtype,
                    task=task)
            return JsonResponse({
                "ok":
                True,
                "latitude":
                latitude,
                "longitude":
                longitude,
                "check_date":
                date_format(timezone.localtime(check_date), 'DATETIME_FORMAT')
            })
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
            return JsonResponse({
                "ok":
                True,
                "finished_date":
                date_format(
                    timezone.localtime(finished_date), 'DATETIME_FORMAT')
            })
        return JsonResponse({"ok": False})


@login_required
def ecm_batch_download(request, pk):
    # https://stackoverflow.com/questions/12881294/django-create-a-zip-of-multiple-files-and-make-it-downloadable
    # http://mypythondjango.blogspot.com/2018/01/how-to-zip-files-in-filefield-and.html
    task = Task.objects.get(pk=pk)
    try:
        buff = io.BytesIO()
        zf = ZipFile(buff, mode='a')
        zip_filename = 'Anexos_OS_{}.zip'.format(task.task_number)
        for ecm in get_task_ecms(pk):
            output = io.BytesIO(ecm.get_file_content())
            output.seek(0)
            zf.writestr(ecm.path.name, output.getvalue())
        zf.close()
        buff.seek(0)
        data = buff.read()
        resp = HttpResponse(data, content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    except Exception as e:
        messages.error(request, 'Erro ao baixar todos arquivos.' + str(e))
        return HttpResponseRedirect(ecm.task.get_absolute_url())


class TypeTaskListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = TypeTask
    table_class = TypeTaskTable
    ordering = ('id', )


class TypeTaskCreateView(AuditFormMixin, CreateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'typetask_list'
    permission_required = (CorePermissions.group_admin, )

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class TypeTaskUpdateView(AuditFormMixin, UpdateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'typetask_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TypeTaskDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = TypeTask
    success_url = reverse_lazy('typetask_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'typetask_list'


class GetTypeTaskMainCharacteristics(CustomLoginRequiredView, View):
    def get(self, request, pk):
        type_task_main = TypeTaskMain.objects.filter(pk=pk).first()
        characteristics = type_task_main.characteristics if type_task_main else None
        return JsonResponse({"characteristics": characteristics})


class ExternalTaskView(UpdateView):
    """
    Permite que o um usuario execute acoes em uma determinado 
    OS sem estar logado
    """
    model = Task
    template_name = 'task/external_task.html'
    form_class = TaskDetailForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get(self, request, status=False, task_hash=False, *args, **kwargs):
        self.object = Task.objects.filter(task_hash=task_hash).first()
        custom_settings = CustomSettings.objects.filter(
            office=self.object.office).first()
        request.user = custom_settings.default_user
        set_office_session(request)
        ecms = Ecm.objects.filter(task_id=self.object.id)
        task_history = TaskHistory.objects.filter(
            task_id=self.object.id).order_by('-create_date')
        survey_data = (self.object.type_task.survey.data
                       if self.object.type_task.survey else None)
        self.execution_date = timezone.now()
        return render(
            request, self.template_name, {
                'object': self.object,
                'task': self.object,
                'form': TaskDetailForm(instance=self.object),
                'user': custom_settings.default_user,
                'ecms': ecms,
                'task_history': task_history,
                'survey_data': survey_data,
                'custom_settings': custom_settings
            })

    def post(self, request, task_hash, *args, **kwargs):
        task = Task.objects.filter(task_hash=task_hash).first()
        custom_settings = CustomSettings.objects.filter(office=task.office)
        form = self.form_class(request.POST, instance=task)
        if custom_settings.exists():
            form.instance.alter_user = custom_settings.first().default_user
        form.instance.task_status = TaskStatus[
            self.request.POST['action']] or TaskStatus.INVALID
        if form.is_valid():
            notes = form.cleaned_data['notes'] if form.cleaned_data[
                'notes'] else None
            logger.info('*send_notes_execution_date*: {}'.format(notes))
            execution_date = (form.cleaned_data['execution_date']
                              if form.cleaned_data['execution_date'] else
                              form.initial['execution_date'])
            survey_result = (form.cleaned_data['survey_result']
                             if form.cleaned_data['survey_result'] else
                             form.initial['survey_result'])
            send_notes_execution_date.send(
                sender=self.__class__,
                notes=notes,
                instance=form.instance,
                execution_date=execution_date,
                survey_result=survey_result,
                **{'external_task': True})
            form.instance.__external_task = True
            form.save()
        return HttpResponseRedirect(
            reverse(
                'external-task-detail', args=[form.instance.task_hash.hex]))


class EcmExternalCreateView(CreateView):
    def post(self, request, task_hash, *args, **kwargs):
        files = request.FILES.getlist('path')
        task = Task.objects.filter(task_hash=task_hash).first()
        custom_settings = CustomSettings.objects.filter(
            office=task.office).first()
        request.user = custom_settings.default_user
        data = {'success': False, 'message': exception_create()}

        for file in files:
            file_name = file._name.replace(' ', '_')
            ecm = Ecm(
                path=file,
                task=task,
                exhibition_name=file_name,
                create_user_id=str(request.user.id),
                create_date=timezone.now())

            try:
                ecm.save()
                data = {
                    'success':
                    True,
                    'id':
                    ecm.id,
                    'task_hash':
                    ecm.task.task_hash.hex,
                    'name':
                    str(file),
                    'user':
                    str(self.request.user),
                    'username':
                    str(self.request.user.first_name + ' ' +
                        self.request.user.last_name),
                    'filename':
                    str(ecm.exhibition_name),
                    'task_id':
                    str(task.pk),
                    'message':
                    success_sent()
                }

            except OperationalError:
                data = {
                    'success': False,
                    'message': operational_error_create()
                }

            except IOError:

                data = {'is_deleted': False, 'message': ioerror_create()}

            except Exception:
                data = {'success': False, 'message': exception_create()}

        return JsonResponse(data)


class ImportTaskList(PermissionRequiredMixin, CustomLoginRequiredView,
                     TemplateView):
    permission_required = ('core.group_admin', )
    template_name = 'task/import_task_list.html'
    form_class = ImportTaskListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_name_plural'] = 'Importação de OS'
        context['page_title'] = 'Importação de OS'
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        form = self.form_class(request.POST, request.FILES)
        status = 200
        if form.is_valid():
            file_xls = form.save(commit=False)
            file_xls.office = get_office_session(request)
            file_xls.create_user = request.user
            file_xls.start = timezone.now()
            file_xls.save()

            ret = import_xls_task_list(file_xls.pk)
            file_xls.end = timezone.now()
            file_xls.save()
            file_xls.delete()
        else:
            status = 500
            ret = {'status': 'false', 'message': form.errors}
            messages.error(request, form.errors)
            return JsonResponse(ret, status=status)
        return JsonResponse(json.loads(json.dumps(ret)), status=status)


class BatchChangeTasksView(DashboardSearchView):
    filter_class = BatchChangTaskFilter
    template_name = 'task/batch-change-tasks.html'
    option = ''
    table_class = DashboardStatusTable

    def get(self, request, option, *args, **kwargs):
        self.option = option
        request.option = option
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        task_list, task_filter = self.query_builder()
        self.filter = task_filter
        if self.option in ['A', 'D']:
            status_to_filter = [TaskStatus.ACCEPTED_SERVICE, TaskStatus.REQUESTED]
            return task_list.filter(task_status__in=status_to_filter)
        status_to_filter = [TaskStatus.ACCEPTED_SERVICE, TaskStatus.REQUESTED, TaskStatus.OPEN,
            TaskStatus.DONE, TaskStatus.ERROR]
        return task_list.filter(task_status__in=status_to_filter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context[self.context_filter_name] = self.filter
        table = self.table_class(self.object_list)
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        context['option'] = self.option
        context['office'] = get_office_session(self.request)
        return context


class BatchServicePriceTable(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        datas = []
        tasks = Task.objects.filter(pk__in=request.GET.getlist('task_ids[]'))
        for task in tasks:
            price_table = CorrespondentsTable(task, task.office)
            cheapest_correspondent = price_table.get_cheapest_correspondent()
            prices = [ {
                'id': price.id,
                'court_district': {
                    'id': price.court_district.pk if price.court_district else '-',
                    'name': price.court_district.name if price.court_district else '-',
                },
                'court_district_complement': {
                    'id': price.court_district_complement.pk if price.court_district_complement else '-',
                    'name': price.court_district_complement.name if price.court_district_complement else '-',
                    },
                'create_user': price.create_user.pk,
                'client': price.client if price.client else '-',
                'city': price.city.name if price.city else '-',
                'office': {
                    'id': price.office.pk,
                    'legal_name': price.office.legal_name
                },
                'office_correspondent': {
                    'id': price.office_correspondent.pk,
                    'legal_name': price.office_correspondent.legal_name
                },
                'state': price.state.initials if price.state else '-',
                'type_task': {
                    'id': price.type_task.pk if price.type_task else '-',
                    'name': price.type_task.name if price.type_task else '-'
                },
                'office_rating': price.office_rating,
                'office_return_rating': price.office_return_rating,
                'value': price.value

            } for price in price_table.correspondents_qs]

            data = {
                'task': {
                    'id': task.pk,
                    'type_task': {
                        'id': task.type_task.pk,
                        'name': task.type_task.name
                    }
                },
                'prices': prices,
                'cheapest_correspondent': {
                    'count': len(price_table.correspondents_qs),
                    'id': cheapest_correspondent.pk if cheapest_correspondent else '',
                    'office_correspondent': cheapest_correspondent.office_correspondent.legal_name if cheapest_correspondent else '',
                    'value': cheapest_correspondent.value if cheapest_correspondent else ''
                }
            }
            datas.append(data)
        return JsonResponse(datas, safe=False)


class BatchCheapestCorrespondent(CustomLoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        task = Task.objects.get(pk=request.GET.get('task_id'))
        price_table = CorrespondentsTable(task, task.office)
        cheapest_correspondent = price_table.get_cheapest_correspondent()
        if cheapest_correspondent:
            return JsonResponse({
                    'count': len(cheapest_correspondent),
                    'id': cheapest_correspondent[0].pk,
                    'office_correspondent': cheapest_correspondent[0].office_correspondent.legal_name,
                    'value': cheapest_correspondent[0].value
                })
        return JsonResponse({})


class ViewTaskToPersonCompanyRepresentative(DashboardSearchView):    
    template_name = 'task/task_to_person_company_representative.html'

    def get_queryset(self):
        task_list, task_filter = self.query_builder()
        self.filter = task_filter                
        return task_list.filter(
            person_company_representative=self.request.user.person).exclude(
            pk__in=self.request.user.tasksurveyanswer_create_user.values_list('task_id', flat=True))

    def get_context_data(self):
        context = super().get_context_data()
        context['surveys'] = [
            {'task_id': task.pk, 'survey': task.type_task.survey} for task in self.object_list
        ]        
        return context        

    def post(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(pk=request.POST.get('task_id'))
            survey_result = json.loads(request.POST.get('survey'))
            survey = TaskSurveyAnswer(create_user=request.user, task=task, survey_result=survey_result)
            survey.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': e})     
            