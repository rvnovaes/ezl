from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
# http://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_tables2 import SingleTableView, RequestConfig

from core.forms import PersonForm
from core.messages import new_success, update_success, delete_error_protected, delete_success
from core.models import Person
from core.tables import PersonTable


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/inicial')
    else:
        return render(request, 'account/login.html')


@login_required
def inicial(request):
    if request.user.is_authenticated:
        title_page = {'title_page': 'Principal - Easy Lawyer'}
        return render(request, 'task/task_dashboard.html', title_page)
    else:
        return HttpResponseRedirect('/')


def logout_user(request):
    # Faz o logout do usuário contido na requisição, limpando todos os dados da sessão corrente;
    logout(request)
    # Redireciona para a página de login
    return HttpResponseRedirect('/')


# Implementa a alteração da data e usuários para operação de update e new
class BaseCustomView(FormView):
    success_url = None

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)
        if form.instance.id is None:
            form.instance.create_date = timezone.now()
            form.instance.create_user = user
        else:
            form.instance.alter_date = timezone.now()
            form.instance.alter_user = user
            form.save()
        super(BaseCustomView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)


class SingleTableViewMixin(SingleTableView):
    def get_context_data(self, **kwargs):
        context = super(SingleTableViewMixin, self).get_context_data(**kwargs)
        context['nav_' + self.model._meta.verbose_name] = True
        context['form_name'] = self.model._meta.verbose_name
        context['form_name_plural'] = self.model._meta.verbose_name_plural
        table = self.table_class(self.model.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


class MultiDeleteViewMixin(DeleteView):
    success_message = None

    def delete(self, request, *args, **kwargs):
        if request.method == "POST":
            pks = request.POST.getlist("selection")
            try:
                self.model.objects.filter(pk__in=pks).delete()
                messages.success(self.request, self.success_message)
            except ProtectedError as e:
                qs = e.protected_objects.first()
                # type = type('Task')
                messages.error(self.request,
                               delete_error_protected(self.model._meta.verbose_name
                                                      , qs.__str__()))
        return HttpResponseRedirect(
            self.success_url)  # http://django-tables2.readthedocs.io/en/latest/pages/generic-mixins.html


@method_decorator(login_required, name='dispatch')
class PersonListView(SingleTableView):
    model = Person
    table_class = PersonTable
    queryset = Person.objects.filter(is_active=True)
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)
        context['nav_person'] = True
        table = PersonTable(Person.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


@method_decorator(login_required, name='dispatch')
class PersonCreateView(SuccessMessageMixin, BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = new_success


@method_decorator(login_required, name='dispatch')
class PersonUpdateView(SuccessMessageMixin, BaseCustomView, UpdateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = update_success


@method_decorator(login_required, name='dispatch')
class PersonDeleteView(BaseCustomView, MultiDeleteViewMixin):
    model = Person
    success_url = reverse_lazy('person_list')
    success_message = delete_success(model._meta.verbose_name_plural)
    # def delete(self, request, *args, **kwargs):
    #     person = self.get_object()
    #     success_url = self.get_success_url()
    #     person_id = int(person.id)
    #     Person.objects.filter(id=person_id).update(active=False)
    #     return HttpResponseRedirect(success_url)
