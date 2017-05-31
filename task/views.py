from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView, TemplateView
from django_tables2 import SingleTableView, RequestConfig, MultiTableMixin

from core.messages import new_success, update_success
from core.models import Person
from core.views import BaseCustomView
from task.forms import TaskForm
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
    success_url = reverse_lazy('task-list')

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_id = int(task.id)
        Task.objects.filter(id=task_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class DashboardView(MultiTableMixin, TemplateView):
    template_name = "task/task_dashboard.html"

    def load_task_by_status(self, status, person):
        global data
        if status == TaskStatus.OPEN:
            data = Task.objects.filter(execution_date__isnull=True, acceptance_date__isnull=True)
        elif status == TaskStatus.ACCEPTED:
            data = Task.objects.filter(acceptance_date__isnull=False)
        elif status == TaskStatus.RETURN:
            data = Task.objects.filter(return_date__isnull=False)
        elif status == TaskStatus.DONE:
            data = Task.objects.filter(execution_date__isnull=False)
        elif status == TaskStatus.REFUSED:
            data = Task.objects.filter(refused_date__isnull=False)

        if person.is_correspondent:
            return data.filter(person_executed_by=person.id)
        else:
            return data.filter(person_asked_by=person.id)

    def config_table(self, table):
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)

    def get_context_data(self, **kwargs):
        # super(DashboardView, self).get_context_data(**kwargs)
        person = Person.objects.get(auth_user=self.request.user)

        return_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.RETURN, person), title="Retorno")
        accepted_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.ACCEPTED, person), title="Aceitas")
        open_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.OPEN, person), title="Abertas")
        done_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.DONE, person), title="Cumpridas")
        refused_table = DashboardStatusTable(self.load_task_by_status(TaskStatus.REFUSED, person), title="Recusadas")

        self.config_table(return_table)
        self.config_table(accepted_table)
        self.config_table(open_table)
        self.config_table(done_table)
        self.config_table(refused_table)

        self.tables = [return_table, accepted_table, open_table, done_table, refused_table]
        # context['tables'] = tables
        return super(DashboardView, self).get_context_data(**kwargs)
