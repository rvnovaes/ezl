import os
from urllib.parse import urlparse
import json
from chat.models import UserByChat
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError, OperationalError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin

from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, \
    operational_error_create, ioerror_create, exception_create, \
    integrity_error_delete, \
    DELETE_EXCEPTION_MESSAGE, success_sent, success_delete, NO_PERMISSIONS_DEFINED
from core.models import Person
from core.views import AuditFormMixin, MultiDeleteViewMixin, SingleTableViewMixin
from etl.models import InconsistencyETL
from etl.tables import DashboardErrorStatusTable
from lawsuit.models import Movement, CourtDistrict
from task.filters import TaskFilter
from task.forms import TaskForm, TaskDetailForm, TypeTaskForm, TaskCreateForm
from task.models import Task, TaskStatus, Ecm, TypeTask, TaskHistory, DashboardViewModel
from task.signals import send_notes_execution_date
from task.tables import TaskTable, DashboardStatusTable, TypeTaskTable
from financial.models import ServicePriceTable
from chat.models import Chat
from financial.tables import ServicePriceTableTaskTable

class TaskListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Task
    table_class = TaskTable


class TaskCreateView(AuditFormMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    success_url = reverse_lazy('task_list')
    success_message = CREATE_SUCCESS_MESSAGE
    template_name_suffix = '_create_form'

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

    def form_valid(self, form):
        task = form.instance
        form.instance.movement_id = self.kwargs.get('movement')
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        form.instance.__server = self.request.META['HTTP_HOST']
        response = super(TaskCreateView, self).form_valid(form)

        if form.cleaned_data['documents']:
            for document in form.cleaned_data['documents']:
                task.ecm_set.create(path=document,
                                    create_user=task.create_user)

        form.delete_temporary_files()

        return response

    def get_success_url(self):
        return reverse('movement_update',
                       kwargs={'lawsuit': self.kwargs['lawsuit'],
                               'pk': self.kwargs['movement']})


class TaskUpdateView(AuditFormMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')
    success_message = UPDATE_SUCCESS_MESSAGE

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

    def form_valid(self, form):
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        form.instance.__server = self.request.META['HTTP_HOST']
        super(TaskUpdateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse('movement_update',
                                   kwargs={'lawsuit': self.kwargs['lawsuit'],
                                           'pk': self.kwargs['movement']})
        super(TaskUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)

        return context


class TaskDeleteView(SuccessMessageMixin, LoginRequiredMixin, MultiDeleteViewMixin):
    model = Task
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)

    def post(self, request, *args, **kwargs):
        self.success_url = urlparse(request.environ.get('HTTP_REFERER')).path
        return super(TaskDeleteView, self).post(request, *args, **kwargs)


class DashboardView(MultiTableMixin, TemplateView):
    template_name = 'task/task_dashboard.html'
    table_pagination = {
        'per_page': 5
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if not self.request.user.get_all_permissions():
            context['messages'] = [
                {'tags': 'error', 'message': NO_PERMISSIONS_DEFINED}
            ]
        return context

    def get_tables(self):
        person = Person.objects.get(auth_user=self.request.user)
        dynamic_query = self.get_dynamic_query(person)
        data = []
        # NOTE: Quando o usuário é superusuário ou não possui permissão é retornado um objeto Q vazio
        if dynamic_query or person.auth_user.is_superuser:
            data = DashboardViewModel.objects.filter(dynamic_query)

        if person.auth_user.groups.filter(~Q(name='Correspondente')).exists():
            data = data | DashboardViewModel.objects.filter(
                task_status__in=[TaskStatus.REQUESTED, TaskStatus.REFUSED_SERVICE,
                                 TaskStatus.ACCEPTED_SERVICE, TaskStatus.ERROR])

        tables = self.get_list_tables(data, person) if person else []
        if not dynamic_query:
            return tables
        return tables

    @staticmethod
    def get_list_tables(data, person):
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
        error = InconsistencyETL.objects.filter(is_active=True) or {}

        return_list = []

        if not person.auth_user.has_perm('core.view_delegated_tasks') or person.auth_user.is_superuser:
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
        return Q(person_distributed_by=person.id)

    def get_dynamic_query(self, person):
        if person.auth_user.is_superuser:
            return self.get_query_all_tasks(person)
        dynamic_query = Q()
        permissions_to_check = {
            'core.view_all_tasks': self.get_query_all_tasks,
            'core.view_delegated_tasks': self.get_query_delegated_tasks,
            'core.view_distributed_tasks': self.get_query_distributed_tasks,
            'core.view_requested_tasks': self.get_query_requested_tasks
        }
        for permission in person.auth_user.get_all_permissions():
            if permission in permissions_to_check.keys():
                dynamic_query |= permissions_to_check.get(permission)(person)
        return dynamic_query


class TaskDetailView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskDetailForm
    success_url = reverse_lazy('dashboard')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name = 'task/task_detail.html'

    def form_valid(self, form):
        execution_date = None
        form.instance.task_status = TaskStatus[self.request.POST['action']] or TaskStatus.INVALID
        form.instance.alter_user = User.objects.get(id=self.request.user.id)
        notes = form.cleaned_data['notes'] if form.cleaned_data['notes'] else None
        if form.cleaned_data['execution_date'] and not form.instance.execution_date:
            execution_date = form.cleaned_data['execution_date']
        survey_result = (form.cleaned_data['survey_result']
                         if form.cleaned_data['survey_result'] else None)

        send_notes_execution_date.send(sender=self.__class__, notes=notes, instance=form.instance,
                                       execution_date=execution_date, survey_result=survey_result)
        form.instance.__server = self.request.META['HTTP_HOST']
        if form.instance.task_status == TaskStatus.ACCEPTED_SERVICE:
            form.instance.acceptance_service_date = timezone.now()
        if form.instance.task_status == TaskStatus.REFUSED_SERVICE:
            form.instance.refused_service_date = timezone.now()
        if form.instance.task_status == TaskStatus.OPEN:
            form.instance.amount = form.cleaned_data['amount']
            servicepricetable_id = self.request.POST['servicepricetable_id']
            servicepricetable = ServicePriceTable.objects.get(id=servicepricetable_id)
            form.instance.person_executed_by = (servicepricetable.correspondent
                                                if servicepricetable.correspondent else None)
        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)
        context['task_history'] = \
            TaskHistory.objects.filter(task_id=self.object.id).order_by('-create_date')

        # Atualiza ou cria o chat, (Eh necessario encontrar um lugar melhor para este bloco de codigo)
        state = ''
        if isinstance(self.object.court_district, CourtDistrict):
            state = self.object.court_district.state
        opposing_party = ''
        if self.object.movement and self.object.movement.law_suit:
            opposing_party = self.object.movement.law_suit.opposing_party
        description = """
        Parte adversa: {opposing_party}, Cliente: {client},
        {court_district} - {state}, Prazo: {final_deadline_date}
        """.format(opposing_party=opposing_party, client=self.object.client,
        court_district=self.object.court_district, state=state,
        final_deadline_date=self.object.final_deadline_date.strftime('%d/%m/%Y %H:%M'))
        if self.object.chat:
            self.object.chat.description = description
            self.object.chat.save()
        else:
            label = 'task-{}'.format(self.object.pk)
            title = """#{task_number} - {type_task}""".format(
            task_number=self.object.task_number, type_task=self.object.type_task)
            self.object.chat = Chat.objects.create(
                create_user=self.request.user, label=label, title=title,
                description=description, back_url='/dashboard/{}'.format(self.object.pk))
            self.object.save()
        self.create_user_by_chat(self.object, ['person_asked_by', 'person_executed_by',
                                               'person_distributed_by'])
        type_task = self.object.type_task
        court_district = self.object.movement.law_suit.court_district
        state = self.object.movement.law_suit.court_district.state
        client = self.object.movement.law_suit.folder.person_customer
        context['correspondents_table'] = ServicePriceTableTaskTable(
            ServicePriceTable.objects.filter(Q(type_task=type_task),
                                             Q(Q(court_district=court_district) | Q(court_district=None)),
                                             Q(Q(state=state) | Q(state=None)),
                                             Q(Q(client=client) | Q(client=None)))
        )
        return context

    def create_user_by_chat(self, task, fields):
        for field in fields:
            user = getattr(task, field).auth_user
            if user:
                UserByChat.objects.get_or_create(user_by_chat=user, chat=task.chat, defaults={
                    'create_user': user, 'user_by_chat': user, 'chat': task.chat
                })


class EcmCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):

        files = request.FILES.getlist('path')
        task = kwargs['pk']
        data = {'success': False,
                'message': exception_create()}

        data = {'success': False,
                'message': exception_create()
                }
        for file in files:

            ecm = Ecm(path=file,
                      task=Task.objects.get(id=task),
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
                        'filename': str(os.path.basename(ecm.path.path)),
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


class TypeTaskListView(LoginRequiredMixin, SingleTableViewMixin):
    model = TypeTask
    table_class = TypeTaskTable


class TypeTaskCreateView(AuditFormMixin, CreateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
    success_message = CREATE_SUCCESS_MESSAGE


class TypeTaskUpdateView(AuditFormMixin, UpdateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
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
        cache.set('type_task_page', self.request.META.get('HTTP_REFERER'))
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
        if cache.get('type_task_page'):
            self.success_url = cache.get('type_task_page')

        return super().post(request, *args, **kwargs)


class TypeTaskDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = TypeTask
    success_url = reverse_lazy('typetask_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)


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


class DashboardSearchView(LoginRequiredMixin, SingleTableView):
    model = DashboardViewModel
    filter_class = TaskFilter
    template_name = 'task/task_filter.html'
    context_object_name = 'task_filter'
    context_filter_name = 'filter'
    ordering = ['-final_deadline_date']
    table_class = DashboardStatusTable

    def query_builder(self):
        query_set = {}
        person = Person.objects.get(auth_user=self.request.user)

        request = self.request.GET
        task_filter = TaskFilter(request)
        task_form = task_filter.form

        if task_form.is_valid():
            data = task_form.cleaned_data
            task_dynamic_query = Q()
            person_dynamic_query = Q()
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

            if not self.request.user.has_perm('core.view_all_tasks'):
                if self.request.user.has_perm('core.view_delegated_tasks'):
                    person_dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
                elif self.request.user.has_perm('core.view_requested_tasks'):
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
            if data['law_suit_number']:
                task_dynamic_query.add(Q(movement__law_suit__law_suit_number=data['law_suit_number']), Q.AND)
            if data['task_number']:
                task_dynamic_query.add(Q(task_number=data['task_number']), Q.AND)
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
                        Q(acceptance_service_date__gte=data['accepted_service_in'].start.replace(hour=0, minute=0)), Q.AND)
                if data['accepted_service_in'].stop:
                    accepted_service_dynamic_query.add(
                        Q(acceptance_service_date__lte=data['accepted_service_in'].stop.replace(hour=23, minute=59)), Q.AND)
            if data['refused_service_in']:
                if data['refused_service_in'].start:
                    refused_service_query.add(
                        Q(refused_service_date__gte=data['refused_service_in'].start.replace(hour=0, minute=0)), Q.AND)
                if data['refused_service_in'].stop:
                    refused_service_query.add(
                        Q(refused_service_date__lte=data['refused_service_in'].stop.replace(hour=23, minute=59)), Q.AND)
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
                        Q(blocked_payment_date__gte=data['blocked_payment_in'].start.replace(hour=0, minute=0)), Q.AND)
                if data['blocked_payment_in'].stop:
                    blocked_payment_dynamic_query.add(
                        Q(blocked_payment_date__lte=data['blocked_payment_in'].stop.replace(hour=23, minute=59)), Q.AND)
            if data['finished_in']:
                if data['finished_in'].start:
                    finished_dynamic_query.add(
                        Q(finished_date__gte=data['finished_in'].start.replace(hour=0, minute=0)), Q.AND)
                if data['finished_in'].stop:
                    finished_dynamic_query.add(
                        Q(finished_date__lte=data['finished_in'].stop.replace(hour=23, minute=59)), Q.AND)

            person_dynamic_query.add(Q(client_query), Q.AND)\
                .add(Q(task_dynamic_query), Q.AND)\
                .add(Q(requested_dynamic_query), Q.AND)\
                .add(Q(accepted_service_dynamic_query), Q.AND)\
                .add(Q(refused_service_query), Q.AND)\
                .add(Q(open_dynamic_query), Q.AND)\
                .add(Q(accepted_dynamic_query), Q.AND)\
                .add(Q(refused_dynamic_query), Q.AND)\
                .add(Q(return_dynamic_query), Q.AND)\
                .add(Q(done_dynamic_query), Q.AND)\
                .add(Q(blocked_payment_dynamic_query), Q.AND)\
                .add(Q(finished_dynamic_query), Q.AND)

            query_set = DashboardViewModel.objects.filter(person_dynamic_query)

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


class DashboardStatusCheckView(LoginRequiredMixin, View):

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
