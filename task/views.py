from datetime import datetime

import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin

from core.messages import new_success, update_success
from core.models import Person
from core.views import BaseCustomView
from ezl import settings
from task.forms import TaskForm, TaskDetailForm
from task.models import Task, TaskStatus
from task.tables import TaskTable, DashboardStatusTable


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
        global data
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

        if person.is_correspondent:
            return data.filter(person_executed_by=person.id)
        else:
            return data.filter(person_asked_by=person.id)

    def get_tables(self):

        person = Person.objects.get(auth_user=self.request.user)
        if person:
            return_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.RETURN, person), title="Retornadas",
                                                status=TaskStatus.RETURN)

            accepted_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.ACCEPTED, person),
                                                  title="A Cumprir", status=TaskStatus.ACCEPTED)

            open_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.OPEN, person), title="Em Aberto",
                                              status=TaskStatus.OPEN)

            done_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.DONE, person), title="Cumpridas",
                                              status=TaskStatus.DONE)

            refused_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.REFUSED, person),
                                                 title="Recusadas", status=TaskStatus.REFUSED)

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
        now_date = datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
        action = self.request.POST['action']

        if action == TaskStatus.ACCEPTED.name:
            task.acceptance_date = now_date
        elif action == TaskStatus.REFUSED.name:
            task.refused_date = now_date
        elif action == TaskStatus.DONE.name:
            if form.cleaned_data['execution_date']:
                task.execution_date = form.cleaned_data['execution_date']
                # else:
                #     task.execution_date =
        elif action == TaskStatus.RETURN.name:
            task.execution_date = None
            task.refused_date = now_date
        task.alter_date = now_date
        task.alter_user = User.objects.get(id=self.request.user.id)
        form = TaskDetailForm(self.request.POST, instance=task)
        form.save()
        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)
