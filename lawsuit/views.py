from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
# project imports
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django_tables2 import RequestConfig

from core.views import BaseCustomView
from .forms import TypeMovementForm, InstanceForm, MovementForm, FolderForm, LawSuitForm, TaskForm
from .models import TypeMovement, Instance, Movement, LawSuit, Folder, Task
from .tables import TypeMovementTable, MovementTable, FolderTable, LawSuitTable, TaskTable


class InstanceUpdateView(BaseCustomView, UpdateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceDeleteView(BaseCustomView, DeleteView):
    model = Instance
    success_url = reverse_lazy('instance_list')

    # Sobrescreve a função Delete da classe DeleteView. Pois a exclusão de um elemento é
    # Tornar o flag Active = False e não remover a linha
    def delete(self, request, *args, **kwargs):

        instance = self.get_object()
        success_url = self.success_url
        instance_id = int(instance.id)
        Instance.objects.filter(id=instance_id).update(active=False)
        return HttpResponseRedirect(success_url)


class InstanceCreateView(BaseCustomView, CreateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceListView(ListView):
    model = Instance
    queryset = Instance.objects.filter(active=True)


class TypeMovementListView(ListView):
    model = TypeMovement
    queryset = TypeMovement.objects.filter(active=True)
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(TypeMovementListView, self).get_context_data(**kwargs)
        context['nav_type_movement'] = True
        table = TypeMovementTable(TypeMovement.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class TypeMovementCreateView(BaseCustomView, CreateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')


class TypeMovementUpdateView(BaseCustomView, UpdateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')


class TypeMovementDeleteView(BaseCustomView, DeleteView):
    model = TypeMovement
    success_url = reverse_lazy('type_movement_list')

    def delete(self, request, *args, **kwargs):
        typemovement = self.get_object()
        typemovement_id = int(typemovement.id)
        TypeMovement.objects.filter(id=typemovement_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class MovementListView(ListView):
    model = Movement
    queryset = Movement.objects.filter(active=True)
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super(MovementListView, self).get_context_data(**kwargs)
        context['nav_movement'] = True
        table = MovementTable(Movement.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class MovementCreateView(BaseCustomView, CreateView):
    model = Movement
    form_class = MovementForm
    success_url = reverse_lazy('movement_list')


class MovementUpdateView(BaseCustomView, UpdateView):
    model = Movement
    form_class = MovementForm
    success_url = reverse_lazy('movement_list')


class MovementDeleteView(BaseCustomView, DeleteView):
    model = Movement
    success_url = reverse_lazy('movement_list')

    def delete(self, request, *args, **kwargs):
        movement = self.get_object()
        movement_id = int(movement.id)
        Movement.objects.filter(id=movement_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class FolderListView(BaseCustomView, ListView):
    model = Folder
    queryset = Folder.objects.filter(active=True)
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(FolderListView, self).get_context_data(**kwargs)
        context['nav_folder'] = True
        table = FolderTable(Folder.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class FolderCreateView(BaseCustomView, CreateView):
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folder_list')


class FolderUpdateView(BaseCustomView, UpdateView):
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folder_list')


class FolderDeleteView(BaseCustomView, DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')

    def delete(self, request, *args, **kwargs):
        folder = self.get_object()
        folder_id = int(folder.id)
        Movement.objects.filter(id=folder_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class LawSuitListView(ListView):
    model = LawSuit
    queryset = LawSuit.objects.filter(active=True)
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super(LawSuitListView, self).get_context_data(**kwargs)
        context['nav_lawsuit'] = True
        table = LawSuitTable(LawSuit.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class LawSuitCreateView(BaseCustomView, CreateView):
    model = LawSuit
    form_class = LawSuitForm
    success_url = reverse_lazy('lawsuit-list')


class LawSuitUpdateView(BaseCustomView, UpdateView):
    model = LawSuit
    form_class = LawSuitForm
    success_url = reverse_lazy('lawsuit-list')


class LawSuitDeleteView(BaseCustomView, DeleteView):
    model = LawSuit
    success_url = reverse_lazy('lawsuit_list')

    def delete(self, request, *args, **kwargs):
        lawsuit = self.get_object()
        lawsuit_id = int(lawsuit.id)
        LawSuit.objects.filter(id=lawsuit_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class TaskListView(BaseCustomView, ListView):
    model = Task
    queryset = Task.objects.filter(active=True)
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['nav_task'] = True
        table = TaskTable(Task.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class TaskCreateView(BaseCustomView, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')


class TaskUpdateView(BaseCustomView, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')


class TaskDeleteView(BaseCustomView, DeleteView):
    model = Task
    success_url = reverse_lazy('task-list')

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_id = int(task.id)
        Movement.objects.filter(id=task_id).update(active=False)
        return HttpResponseRedirect(self.success_url)
