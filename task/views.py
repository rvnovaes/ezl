import os
# from .utils import PagedFilteredTableView
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin

from core.messages import new_success, update_success, delete_success
from core.models import Person
from core.views import BaseCustomView, MultiDeleteViewMixin, SingleTableViewMixin

from .forms import TaskForm, TaskDetailForm, EcmForm, TypeTaskForm
from .models import Task, TaskStatus, Ecm, TaskHistory, TypeTask
from .tables import TaskTable, DashboardStatusTable, TypeTaskTable
from .filters import TaskFilter
from django.db import IntegrityError, DataError, OperationalError
from core.messages import operational_error_create, ioerror_create, exception_create, integrity_error_delete, \
    file_exists_error_delete, exception_delete, success_sent, success_delete


class TaskListView(LoginRequiredMixin, SingleTableView):
    model = Task
    table_class = TaskTable
    queryset = Task.objects.all()
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['nav_task'] = True
        table = TaskTable(Task.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


class TaskCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')
    success_message = new_success

    def get_initial(self):
        if isinstance(self, TaskCreateView):
            self.form_class.declared_fields['task_status'].initial = 'OPEN'
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True


class TaskUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')
    success_message = update_success


class TaskDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')


class DashboardView(MultiTableMixin, TemplateView):
    template_name = "task/task_dashboard.html"
    table_pagination = {
        'per_page': 5
    }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['title_page'] = u"Dashboard do Correpondente"
        return self.render_to_response(context)

    def load_task_by_status(self, status, person):
        data = {}
        if status == TaskStatus.OPEN:
            data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
                                       refused_date__isnull=True, execution_date__isnull=True, return_date__isnull=True)
        elif status == TaskStatus.ACCEPTED:
            data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                       refused_date__isnull=True, execution_date__isnull=True, return_date__isnull=True)
        elif status == TaskStatus.REFUSED:
            data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
                                       refused_date__isnull=False, execution_date__isnull=True,
                                       return_date__isnull=True)
        elif status == TaskStatus.DONE:
            data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                       refused_date__isnull=True, execution_date__isnull=False,
                                       return_date__isnull=True)
        elif status == TaskStatus.RETURN:
            data = Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                       refused_date__isnull=True, execution_date__isnull=True,
                                       return_date__isnull=False)
        # TODO Adicionar metodo para filtrar dashboard do coordenador
        if person.is_correspondent:
            return data.filter(person_executed_by=person.id)
        else:
            return data.filter(person_asked_by=person.id)

    def get_tables(self):

        person = Person.objects.get(auth_user=self.request.user)
        if person:
            return_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.RETURN, person), title="Retornadas",
                                                status=TaskStatus.RETURN, order_by="-alter_date")

            accepted_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.ACCEPTED, person),
                                                  title="A Cumprir", status=TaskStatus.ACCEPTED,
                                                  order_by="-alter_date")

            open_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.OPEN, person), title="Em Aberto",
                                              status=TaskStatus.OPEN, order_by="-alter_date")

            done_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.DONE, person), title="Cumpridas",
                                              status=TaskStatus.DONE, order_by="-alter_date")

            refused_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.REFUSED, person),
                                                 title="Recusadas", status=TaskStatus.REFUSED, order_by="-alter_date"
                                                 )

            tables = [return_table, accepted_table, open_table, done_table, refused_table]
        else:
            tables = None
        return tables


class TaskDetailView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskDetailForm
    success_url = reverse_lazy('dashboard')
    success_message = update_success
    template_name = "task/task_detail.html"

    def form_valid(self, form):
        task = form.instance
        notes = form.cleaned_data['notes']
        now_date = timezone.now()
        action = self.request.POST['action']

        if action == TaskStatus.ACCEPTED.name:
            task.acceptance_date = now_date
        elif action == TaskStatus.REFUSED.name:
            task.refused_date = now_date
        elif action == TaskStatus.DONE.name:
            if form.cleaned_data['execution_date']:
                task.execution_date = form.cleaned_data['execution_date']
                task.return_date = None
                # else:
                #     task.execution_date =
        elif action == TaskStatus.RETURN.name:
            task.execution_date = None
            task.refused_date = now_date

        task.alter_date = now_date
        user = User.objects.get(id=self.request.user.id)
        task.alter_user = user
        status = TaskStatus[action]
        task.task_status = status.name
        form = TaskDetailForm(self.request.POST, instance=task)
        form.save()
        # salvando snapshot com novo status

        task_history = TaskHistory(task=task, create_user=user, create_date=now_date, status=status,
                                   notes=notes)
        task_history.save()

        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['geds'] = Ecm.objects.filter(task_id=self.object.id)
        return context


class EcmCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('path')
        task = kwargs['pk']

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


class TypeTaskListView(LoginRequiredMixin, SingleTableViewMixin):
    model = TypeTask
    table_class = TypeTaskTable

    # def get_context_data(self, **kwargs):
    #     context = super(CourtDistrictListView, self).get_context_data(**kwargs)
    #     context['nav_courtdistrict'] = True
    #     table = CourtDistrictTable(CourtDistrict.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


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
        # query = Ecm.objects.filter(id=pk).delete()
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
        filter = TaskFilter(request)
        task_form = filter.form

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
                    reminder_dynamic_query.add(Q(reminder_deadline_date__gte=data['reminder'].start), Q.AND)
                if data['reminder'].stop:
                    reminder_dynamic_query.add(Q(reminder_deadline_date__lte=data['reminder'].stop), Q.AND)
            if data['deadline']:
                if data['deadline'].start:
                    deadline_dynamic_query.add(Q(final_deadline_date__gte=data['deadline'].start), Q.AND)
                if data['deadline'].stop:
                    deadline_dynamic_query.add(Q(final_deadline_date__lte=data['deadline'].stop), Q.AND)

            person_dynamic_query.add(status_dynamic_query, Q.AND).add(Q(reminder_dynamic_query), Q.AND)

            query_set = Task.objects.filter(person_dynamic_query)

            if data['client']:
                wanted_items = set()
                for i in query_set:
                    if request.get('client') in str(i.client):
                        wanted_items.add(i.pk)

                query_set.filter(pk__in=wanted_items)

        return query_set, filter

    def get_queryset(self, **kwargs):
        task_list = {}
        person = Person.objects.get(auth_user=self.request.user)

        if bool(self.request.GET):
            task_list, task_filter = self.query_builder(person)
            # self.table =
            self.filter = task_filter
        else:
            self.filter = TaskFilter(queryset={})
        return task_list

    def get_context_data(self, **kwargs):
        context = super(DashboardSearchView, self).get_context_data()
        # if self.request:
        context[self.context_filter_name] = self.filter
        table = DashboardStatusTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context
