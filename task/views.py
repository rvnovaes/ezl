import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError, OperationalError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, TemplateView
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin

from core.messages import new_success, update_success, delete_success
from core.messages import operational_error_create, ioerror_create, exception_create, integrity_error_delete, \
    file_exists_error_delete, exception_delete, success_sent, success_delete
from core.models import Person
from core.views import BaseCustomView, MultiDeleteViewMixin, SingleTableViewMixin
from lawsuit.models import Movement
from task.signals import send_notes_execution_date
from .filters import TaskFilter
from .forms import TaskForm, TaskDetailForm, TypeTaskForm
from .models import Task, TaskStatus, Ecm, TypeTask, TaskHistory
from .tables import TaskTable, DashboardStatusTable, TypeTaskTable


class TaskListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Task
    table_class = TaskTable


class TaskCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')
    success_message = new_success

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
        form.instance.movement_id = self.kwargs.get('movement')
        self.kwargs.update({'lawsuit': form.instance.movement.law_suit_id})
        super(TaskCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse('movement_update',
                                   kwargs={'lawsuit': self.kwargs['lawsuit'], 'pk': self.kwargs['movement']})
        super(TaskCreateView, self).get_success_url()


class TaskUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')
    success_message = update_success

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
        super(TaskUpdateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse('movement_update',
                                   kwargs={'lawsuit': self.kwargs['lawsuit'], 'pk': self.kwargs['movement']})
        super(TaskUpdateView, self).get_success_url()


class TaskDeleteView(SuccessMessageMixin, LoginRequiredMixin, MultiDeleteViewMixin):
    model = Task
    success_url = reverse_lazy('task_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class DashboardView(MultiTableMixin, TemplateView):
    template_name = "task/task_dashboard.html"
    table_pagination = {
        'per_page': 5
    }

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['title_page'] = u"Dashboard do Correspondente"
        # user_groups = list(group.name for group in self.request.user.groups.all())
        # self.request.session['user_groups'] = user_groups
        # self.request.session['permissions'] = list(
        #     permission.replace("task.", "") for permission in self.request.user.get_all_permissions())
        return context

    # def load_task_by_status(self, status, person):
    #     data = {}
    #     if status == TaskStatus.OPEN:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
    #                                    refused_date__isnull=True, execution_date__isnull=True, return_date__isnull=True,
    #                                    blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=True)
    #     elif status == TaskStatus.ACCEPTED:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
    #                                    refused_date__isnull=True, execution_date__isnull=True, return_date__isnull=True,
    #                                    blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=True)
    #     elif status == TaskStatus.REFUSED:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
    #                                    refused_date__isnull=False, execution_date__isnull=True,
    #                                    return_date__isnull=True, blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=True)
    #     elif status == TaskStatus.DONE:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
    #                                    refused_date__isnull=True, execution_date__isnull=False,
    #                                    return_date__isnull=True, blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=True)
    #     elif status == TaskStatus.RETURN:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
    #                                    refused_date__isnull=True, execution_date__isnull=True,
    #                                    return_date__isnull=False, blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=True)
    #
    #     elif status == TaskStatus.BLOCKEDPAYMENT:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
    #                                    refused_date__isnull=True, execution_date__isnull=False,
    #                                    return_date__isnull=True, blocked_payment_date__isnull=False,
    #                                    finished_date__isnull=True)
    #     elif status == TaskStatus.FINISHED:
    #         data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
    #                                    refused_date__isnull=True, execution_date__isnull=False,
    #                                    return_date__isnull=True, blocked_payment_date__isnull=True,
    #                                    finished_date__isnull=False)
    #     # TODO Adicionar metodo para filtrar dashboard do coordenador
    #     if person.is_correspondent:
    #         return data.filter(person_executed_by=person.id)
    #     else:
    #         return data.filter(person_asked_by=person.id)

    def get_tables(self):

        dynamic_query = Q()
        person = Person.objects.get(auth_user=self.request.user)
        if self.request.user.has_perm('task.view_all_tasks'):
            dynamic_query.add(Q(delegation_date__isnull=False), Q.AND)
        else:
            if self.request.user.has_perm('task.view_delegated_tasks'):
                dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
            elif self.request.user.has_perm('task.view_requested_tasks'):
                dynamic_query.add(Q(person_asked_by=person.id), Q.AND)
        self.request.user.get_all_permissions()
        data = Task.objects.filter(dynamic_query)
        # print(str(Task.objects.filter(dynamic_query).query))
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

        if person:
            return_table = DashboardStatusTable(returned, title="Retornadas",
                                                status=TaskStatus.RETURN)

            accepted_table = DashboardStatusTable(accepted,
                                                  title="A Cumprir", status=TaskStatus.ACCEPTED,
                                                  order_by="-alter_date")

            open_table = DashboardStatusTable(opened, title="Em Aberto",
                                              status=TaskStatus.OPEN, order_by="-alter_date")

            done_table = DashboardStatusTable(done, title="Cumpridas",
                                              status=TaskStatus.DONE, order_by="-alter_date")

            refused_table = DashboardStatusTable(refused,
                                                 title="Recusadas", status=TaskStatus.REFUSED, order_by="-alter_date"
                                                 )
            blocked_payment_table = DashboardStatusTable(blocked_payment,
                                                         title="Glosadas", status=TaskStatus.BLOCKEDPAYMENT,
                                                         order_by="-alter_date"
                                                         )
            finished_table = DashboardStatusTable(finished,
                                                  title="Finalizadas", status=TaskStatus.FINISHED,
                                                  order_by="-alter_date"
                                                  )

            tables = [return_table, accepted_table, open_table, done_table, refused_table, blocked_payment_table,
                      finished_table]
        else:
            tables = {}
        return tables


class TaskDetailView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskDetailForm
    success_url = reverse_lazy('dashboard')
    success_message = update_success
    template_name = "task/task_detail.html"

    def form_valid(self, form):
        form.instance.task_status = TaskStatus[self.request.POST['action']] or TaskStatus.INVALID
        form.instance.alter_user = User.objects.get(id=self.request.user.id)
        notes = form.cleaned_data['notes'] if form.cleaned_data['notes'] else None
        if form.cleaned_data['execution_date'] and not form.instance.execution_date:
            execution_date = form.cleaned_data['execution_date']
        survey_result = form.cleaned_data['survey_result'] if form.cleaned_data['survey_result'] else None

        send_notes_execution_date.send(sender=self.__class__, notes=notes, instance=form.instance,
                                       execution_date=execution_date, survey_result=survey_result)

        # form.save()

        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url + str(form.instance.id))

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['geds'] = Ecm.objects.filter(task_id=self.object.id)
        context['task_history'] = TaskHistory.objects.filter(task_id=self.object.id).order_by('-create_date')

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
                      create_date=timezone.now()
                      )

            try:
                ecm.save()
                data = {'success': True,
                        'id': ecm.id,
                        'name': str(file),
                        'user': str(self.request.user),
                        'username': str(self.request.user.first_name + ' ' + self.request.user.last_name),
                        'filename': str(os.path.basename(ecm.path.path)),
                        'task_id': str(task),
                        'message': success_sent()
                        }

            except OperationalError:
                data = {'success': False,
                        'message': operational_error_create()
                        }

            except IOError:

                data = {'is_deleted': False,
                        'message': ioerror_create()
                        }

            except Exception:
                data = {'success': False,
                        'message': exception_create()
                        }

        return JsonResponse(data)

        return JsonResponse(data)


class TypeTaskListView(LoginRequiredMixin, SingleTableViewMixin):
    model = TypeTask
    table_class = TypeTaskTable


class TypeTaskCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
    success_message = new_success


class TypeTaskUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = TypeTask
    form_class = TypeTaskForm
    success_url = reverse_lazy('typetask_list')
    success_message = update_success


class TypeTaskDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = TypeTask
    success_url = reverse_lazy('typetask_list')
    success_message = delete_success(model._meta.verbose_name_plural)


@login_required
def delete_ecm(request, pk):
    query = Ecm.objects.filter(id=pk)
    task = query.values('task_id').first()

    try:
        # import_query = Ecm.objects.filter(id=pk).delete()
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

    except FileExistsError:
        data = {'is_deleted': False,
                'message': file_exists_error_delete()
                }


    except Exception:
        data = {'is_deleted': False,
                'message': exception_delete()
                }

    return JsonResponse(data)


class DashboardSearchView(LoginRequiredMixin, SingleTableView):
    model = Task
    filter_class = TaskFilter
    template_name = 'task/task_filter.html'
    context_object_name = 'task_filter'
    context_filter_name = 'filter'
    ordering = ['-id']
    table_class = DashboardStatusTable

    def query_builder(self, person):
        query_set = {}
        request = self.request.GET
        task_filter = TaskFilter(request)
        task_form = task_filter.form

        if task_form.is_valid():
            data = task_form.cleaned_data
            status_dynamic_query = Q()
            person_dynamic_query = Q()
            reminder_dynamic_query = Q()
            deadline_dynamic_query = Q()
            if person.is_correspondent:
                person_dynamic_query.add(Q(person_executed_by=person.id), Q.AND)
            else:
                person_dynamic_query.add(Q(person_asked_by=person.id), Q.AND)

            if data['openned']:
                status_dynamic_query.add(Q(delegation_date__isnull=False, acceptance_date__isnull=True,
                                           refused_date__isnull=True, execution_date__isnull=True,
                                           return_date__isnull=True), Q.OR)
            if data['accepted']:
                status_dynamic_query.add(Q(delegation_date__isnull=False, acceptance_date__isnull=False,
                                           refused_date__isnull=True, execution_date__isnull=True,
                                           return_date__isnull=True), Q.OR)
            if data['refused']:
                status_dynamic_query.add(Q(delegation_date__isnull=False, acceptance_date__isnull=True,
                                           refused_date__isnull=False, execution_date__isnull=True,
                                           return_date__isnull=True), Q.OR)
            if data['done']:
                status_dynamic_query.add(Q(delegation_date__isnull=False, acceptance_date__isnull=False,
                                           refused_date__isnull=True, execution_date__isnull=False,
                                           return_date__isnull=True), Q.OR)
            if data['returned']:
                status_dynamic_query.add(Q(delegation_date__isnull=False, acceptance_date__isnull=False,
                                           refused_date__isnull=True, execution_date__isnull=True,
                                           return_date__isnull=False), Q.OR)
            if data['reminder']:
                if data['reminder'].start:
                    reminder_dynamic_query.add(
                        Q(reminder_deadline_date__gte=data['reminder'].start.replace(hour=0, minute=0)), Q.AND)
                if data['reminder'].stop:
                    reminder_dynamic_query.add(
                        Q(reminder_deadline_date__lte=data['reminder'].stop.replace(hour=23, minute=59)), Q.AND)
            if data['deadline']:
                if data['deadline'].start:
                    deadline_dynamic_query.add(
                        Q(final_deadline_date__gte=data['deadline'].start.replace(hour=0, minute=0)), Q.AND)
                if data['deadline'].stop:
                    deadline_dynamic_query.add(
                        Q(final_deadline_date__lte=data['deadline'].stop.replace(hour=23, minute=59)), Q.AND)

            person_dynamic_query.add(status_dynamic_query, Q.AND).add(Q(reminder_dynamic_query), Q.AND).add(
                Q(deadline_dynamic_query), Q.AND)

            query_set = Task.objects.filter(person_dynamic_query)

            if data['client']:
                query_set = list(filter(lambda x: x.client.pk == data['client'].id, query_set))

        return query_set, task_filter

    def get_queryset(self, **kwargs):
        task_list = {}
        person = Person.objects.get(auth_user=self.request.user)

        if bool(self.request.GET):
            task_list, task_filter = self.query_builder(person)
            self.filter = task_filter
        else:
            if person.is_correspondent:
                task_list = Task.objects.filter(person_executed_by=person)
            self.filter = TaskFilter(queryset={})
        return task_list

    def get_context_data(self, **kwargs):
        context = super(DashboardSearchView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        table = DashboardStatusTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context
