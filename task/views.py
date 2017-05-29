from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, CreateView, UpdateView
from django_tables2 import SingleTableView, RequestConfig

from core.messages import new_success, update_success
from core.views import BaseCustomView
from task.forms import TaskForm
from task.models import Task
from task.tables import TaskTable


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
