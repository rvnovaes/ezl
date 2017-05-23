from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
# http://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View
from django.views.generic.list import ListView
from django_tables2 import RequestConfig
from django_tables2 import SingleTableView

from core.forms import PersonForm
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
        return render(request, 'inicial.html', title_page)
    else:
        return HttpResponseRedirect('/')


def logout_user(request):
    # Faz o logout do usuário contido na requisição, limpando todos os dados da sessão corrente;
    logout(request)
    # Redireciona para a página de login
    return HttpResponseRedirect('/')


# Implementa a alteração da data e usuários para operação de update e new
class BaseCustomView(View):
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


# http://django-tables2.readthedocs.io/en/latest/pages/generic-mixins.html
@method_decorator(login_required, name='dispatch')
class PersonListView(SingleTableView):
    model = Person
    table_class = PersonTable
    queryset = Person.objects.filter(active=True)
    ordering = ['id']


@method_decorator(login_required, name='dispatch')
class PersonCreateView(BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     try:
    #         return super(PersonForm, self).form_valid(form)
    #     except IntegrityError:
    #
    #         if self.object.active:
    #             Person.objects.filter(self)
    #             #form.add_error('unique_name', 'You already have a user by that name')
    #         else:
    #             form.add_error('unique_name', 'You already have a user by that name')
    #         return HttpResponseRedirect(self.success_url)
    #
    # def save(self):
    #     request.session['unique_name'] = self.object.unique_name
    #     super(DataCreate, self).save() < / code >


@method_decorator(login_required, name='dispatch')
class PersonUpdateView(BaseCustomView, UpdateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')


@method_decorator(login_required, name='dispatch')
class PersonDeleteView(BaseCustomView, DeleteView):
    model = Person
    success_url = reverse_lazy('person_list')

    def delete(self, request, *args, **kwargs):
        person = self.get_object()
        success_url = self.get_success_url()
        person_id = int(person.id)
        Person.objects.filter(id=person_id).update(active=False)
        return HttpResponseRedirect(success_url)
