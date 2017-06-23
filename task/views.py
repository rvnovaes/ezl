import os
# from .utils import PagedFilteredTableView
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
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


def TaskFilterAtt(request, person):
    # {'reminder_init_day': ['0'], 'accepted': ['on'], 'deadline_init_year': ['0'], 'done': ['on'], 'deadline_end_year': ['0'], 'deadline_init_day': ['0'], 'reminder_init_month': ['0'], 'deadline_end_day': ['0'], 'deadline_init_month': ['0'], 'refused': ['on'], 'cliente': [''], 'deadline_end_month': ['0'], 'reminder_end_year': ['0'], 'reminder_end_day': ['0'], 'reminder_init_year': ['0'], 'openned': ['on'], 'returned': ['on'], 'reminder_end_month': ['0']}

    task_list = Task.objects.none()

    if person.is_correspondent:
        task_list = Task.objects.filter(person_executed_by=person.id)
    else:
        task_list = Task.objects.filter(person_asked_by=person.id)

    if not bool(task_list):
        return task_list

    del_datetime_init = None
    del_datetime_end = None
    rem_datetime_init = None
    rem_datetime_end = None

    # if request.get('cliente') != '':
    #    task_list &= Task.objects.filter(client=request.get('cliente'))


    if request.get('deadline_init_year') != '0' and request.get('deadline_init_month') != '0' and request.get(
            'deadline_init_day') != '0':
        del_datetime_init = datetime(int(request.get('deadline_init_year')), int(request.get('deadline_init_month')),
                                     int(request.get('deadline_init_day')))

    if request.get('deadline_end_year') != '0' and request.get('deadline_end_month') != '0' and request.get(
            'deadline_end_day') != '0':
        del_datetime_end = datetime(int(request.get('deadline_end_year')), int(request.get('deadline_end_month')),
                                    int(request.get('deadline_end_day')))

    if request.get('reminder_init_year') != '0' and request.get('reminder_init_month') != '0' and request.get(
            'reminder_init_day') != '0':
        rem_datetime_init = datetime(int(request.get('reminder_init_year')), int(request.get('reminder_init_month')),
                                     int(request.get('reminder_init_day')))

    if request.get('reminder_end_year') != '0' and request.get('reminder_end_month') != '0' and request.get(
            'reminder_end_day') != '0':
        rem_datetime_end = datetime(int(request.get('reminder_end_year')), int(request.get('reminder_end_month')),
                                    int(request.get('reminder_end_day')))

    if 'openned' in request:
        task_list &= Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
                                         refused_date__isnull=True, execution_date__isnull=True,
                                         return_date__isnull=True)
    if 'accepted' in request:
        task_list &= Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                         refused_date__isnull=True, execution_date__isnull=True,
                                         return_date__isnull=True)
    if 'refused' in request:
        task_list &= Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=True,
                                         refused_date__isnull=False, execution_date__isnull=True,
                                         return_date__isnull=True)
    if 'done' in request:
        task_list &= Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                         refused_date__isnull=True, execution_date__isnull=False,
                                         return_date__isnull=True)
    if 'returned' in request:
        task_list &= Task.objects.filter(delegation_date__isnull=False, acceptance_date__isnull=False,
                                         refused_date__isnull=True, execution_date__isnull=True,
                                         return_date__isnull=False)


        # task_list &= Task.objects.filter( final_deadline_date__isnull = False, final_deadline_date__range=(del_datetime_init,del_datetime_end))
    # task_list &= Task.objects.filter( reminder_deadline_date__isnull=False,reminder_deadline_date__range=
    #                               (rem_datetime_init,rem_datetime_end))                                 

    if request.get('cliente') != '':

        wanted_items = set()
        for i in task_list:
            if str(i.client) == request.get('cliente'):
                wanted_items.add(i.pk)

        task_list = Task.objects.filter(pk__in=wanted_items)


    return task_list


def TaskListSearch(request):
    task_list = Task.objects.none()

    person = Person.objects.get(auth_user=request.user)
    if person.is_correspondent:
        task_list = Task.objects.filter(person_executed_by=person.id)
    else:
        task_list = Task.objects.filter(person_asked_by=person.id)

    if bool(request.GET):
        task_list = TaskFilterAtt(request.GET, person)

    task_filter = TaskFilter(request=request.GET, queryset=task_list)

    print("Query", request.GET, "Task List", task_list)

    return render(request, 'task/search.html', {'filter': task_filter})  # pode retornar qualquer lista aqui

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
        # now3 =
        # now2 = timezone.now()
        notes = form.cleaned_data['notes']
        # now_date = datetime.utcnow().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
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
        form = TaskDetailForm(self.request.POST, instance=task)
        form.save()
        # salvando snapshot com novo status
        status = TaskStatus[action]
        task_history = TaskHistory(task=task, create_user=user, create_date=now_date, status=status,
                                   notes=notes)
        task_history.save()
        super(TaskDetailView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context['geds'] = Ecm.objects.filter(task_id=self.object.id)
        return context


class EcmCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Ecm
    form_class = EcmForm
    success_url = reverse_lazy('instance_list')

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('path')
        task = kwargs['pk']

        for file in files:
            ecm = Ecm(path=file,
                      task=Task.objects.get(id=task),
                      create_user_id=str(request.user.id),
                      create_date=timezone.now()
                      )
            ecm.save()
            data = {'success': True,
                    'id': ecm.id,
                    'name': str(file),
                    'user': str(self.request.user),
                    'username': str(self.request.user.first_name + ' ' + self.request.user.last_name),
                    'filename': str(os.path.basename(ecm.path.path)),
                    'task_id': str(task)
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
    num_ged = Ecm.objects.filter(task_id=task['task_id']).count()
    try:
        # query = Ecm.objects.filter(id=pk).delete()
        query.delete()
        num_ged = Ecm.objects.filter(task_id=task['task_id']).count()
        data = {'is_deleted': True,
                'num_ged': num_ged
                }
        return JsonResponse(data)

    except ...:
        data = {'is_deleted': False,
                'num_ged': num_ged
                }
        return JsonResponse(data)
