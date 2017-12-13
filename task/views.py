import os
from urllib.parse import urlparse
import json

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
from lawsuit.models import Movement
from task.filters import TaskFilter
from task.forms import TaskForm, TaskDetailForm, TypeTaskForm, TaskCreateForm
from task.models import Task, TaskStatus, Ecm, TypeTask, TaskHistory, DashboardViewModel
from task.signals import send_notes_execution_date
from task.tables import TaskTable, DashboardStatusTable, TypeTaskTable


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
        form.instance.__server = self.request.environ['HTTP_HOST']
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
        form.instance.__server = self.request.environ['HTTP_HOST']
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
        if isinstance(dynamic_query, Q) and dynamic_query:
            data = DashboardViewModel.objects.filter(dynamic_query)
        tables = self.get_list_tables(data) if person else []
        if not dynamic_query:
            return tables
        return tables

    @staticmethod
    def get_list_tables(data):
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
        return_table = DashboardStatusTable(returned, title='Retornadas',
                                            status=TaskStatus.RETURN)

        accepted_table = DashboardStatusTable(accepted,
                                              title='A Cumprir', status=TaskStatus.ACCEPTED
                                              )

        open_table = DashboardStatusTable(opened, title='Em Aberto',
                                          status=TaskStatus.OPEN)

        done_table = DashboardStatusTable(done, title='Cumpridas',
                                          status=TaskStatus.DONE)

        refused_table = DashboardStatusTable(refused,
                                             title='Recusadas', status=TaskStatus.REFUSED)

        blocked_payment_table = DashboardStatusTable(blocked_payment,
                                                     title='Glosadas',
                                                     status=TaskStatus.BLOCKEDPAYMENT)

        finished_table = DashboardStatusTable(finished,
                                              title='Finalizadas',
                                              status=TaskStatus.FINISHED)

        return [return_table, accepted_table, open_table, done_table, refused_table,
                  blocked_payment_table,
                  finished_table]

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

        form.instance.__server = self.request.environ['HTTP_HOST']
        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['ecms'] = Ecm.objects.filter(task_id=self.object.id)
        context['task_history'] = \
            TaskHistory.objects.filter(task_id=self.object.id).order_by('-create_date')

        return context


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
            status_dynamic_query = Q()
            person_dynamic_query = Q()
            reminder_dynamic_query = Q()
            deadline_dynamic_query = Q()
            client_query = Q()

            if not self.request.user.has_perm('core.view_all_tasks'):
                if self.request.user.has_perm('core.view_delegated_tasks'):
                    person_dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
                elif self.request.user.has_perm('core.view_requested_tasks'):
                    person_dynamic_query.add(Q(person_asked_by=person.id), Q.AND)

            if data['openned']:
                status_dynamic_query.add(Q(task_status=TaskStatus.OPEN.value), Q.OR)
            if data['accepted']:
                status_dynamic_query.add(Q(task_status=TaskStatus.ACCEPTED.value), Q.OR)
            if data['refused']:
                status_dynamic_query.add(Q(task_status=TaskStatus.REFUSED.value), Q.OR)
            if data['done']:
                status_dynamic_query.add(Q(task_status=TaskStatus.DONE.value), Q.OR)
            if data['returned']:
                status_dynamic_query.add(Q(task_status=TaskStatus.RETURN.value), Q.OR)
            if data['blocked']:
                status_dynamic_query.add(Q(task_status=TaskStatus.BLOCKEDPAYMENT.value), Q.OR)
            if data['finished']:
                status_dynamic_query.add(Q(task_status=TaskStatus.FINISHED.value), Q.OR)
            if data['deadline']:
                if data['deadline'].start:
                    deadline_dynamic_query.add(
                        Q(final_deadline_date__gte=data['deadline'].start.replace(hour=0,
                                                                                  minute=0)),
                        Q.AND)
                if data['deadline'].stop:
                    deadline_dynamic_query.add(
                        Q(final_deadline_date__lte=data['deadline'].stop.replace(hour=23,
                                                                                 minute=59)),
                        Q.AND)
            if data['client']:
                client_query.add(Q(client=data['client']), Q.AND)
            person_dynamic_query.add(status_dynamic_query, Q.AND).add(Q(reminder_dynamic_query),
                                                                      Q.AND).add(
                Q(deadline_dynamic_query), Q.AND).add(Q(client_query), Q.AND)

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
