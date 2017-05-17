from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View
from django.views.generic.list import ListView
from django.contrib.auth import logout, user_logged_in
from django_tables2 import RequestConfig

from core.models import Person
from core.forms import PersonForm
from core.tables import PersonTable

from datetime import datetime


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home/')
    else:
        return render(request, 'account/login.html')


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    # Recupera o nome do usuário logado no sistema
    # usuario = User.objects.filter(username=request.user).values("username","first_name")
    # Cria um objeto do tipo 'context' => context = {'username': ''}
    # context = usuario.get()

    title_page = "Principal - Easy Lawyer"
    context = {
        'user_name': request.user,
        'title_page': title_page
    }
    return render(request, 'core/home.html', context)


def logout_user(request):
    # Faz o logout do usuário contido na requisição, limpando todos os dados da sessão corrente;
    logout(request)
    # Redireciona para a página de login
    return HttpResponseRedirect('/')


# Implementa a alteração da data e usuários para operação de update e new
class BaseCustomView(View):

    def form_valid(self, form):
        if form.instance.id is None:
            form.instance.create_date = datetime.now()
            form.instance.create_user = User.objects.get(id=self.request.user.id)
        else:
            form.instance.alter_date = datetime.now()
            form.instance.alter_user = User.objects.get(id=self.request.user.id)
            #form.instance.alter_user = self.request.user.id
            form.save()
        super(BaseCustomView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)


class PersonListView(ListView,BaseCustomView):
    model = Person
    queryset = Person.objects.filter(active=True)
    ordering = ['id']
    # context_object_name = 'person'
    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return self.handle_no_permission()
    #     return super(PersonListView, self).dispatch(request, *args, **kwargs)
    # # def get_context_data(self, **kwargs):
    # #     context = super(PersonListView,self).get_context_data(**kwargs)
    # #     context['person_list'] = self.queryset
    # #     return context

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)
        context['nav_person'] = True
        table = PersonTable(Person.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context


class PersonCreateView(BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = '/pessoas/listar'

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


class PersonUpdateView(BaseCustomView, UpdateView):

    model = Person
    form_class = PersonForm
    success_url = '/pessoas/listar'


class PersonDeleteView(BaseCustomView,DeleteView):
    model = Person
    success_url = '/pessoas/listar'

    def delete(self, request, *args, **kwargs):

        person = self.get_object()
        success_url = self.get_success_url()
        person_id = int(person.id)
        Person.objects.filter(id=person_id).update(active=False)
        return HttpResponseRedirect(success_url)
