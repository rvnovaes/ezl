from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_tables2 import SingleTableView, RequestConfig

from core.forms import PersonForm
from core.messages import new_success, update_success, delete_error_protected, delete_success
from core.models import Person
from core.tables import PersonTable


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('dashboard'))
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

    # Lógica que verifica se a requisição é para Create ou Update.
    # Se Create, o botão 'ativar' é desabilitar e valor padrão True
    # Se Update, o botão 'ativar é habilitado para edição e o valor, carregado do banco
    def get_initial(self):

        if isinstance(self, CreateView):
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True

        elif isinstance(self, UpdateView):
            self.form_class.declared_fields['is_active'].disabled = False
        return self.initial.copy()

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)
        if form.instance.id is None:
            # todo: nao precisa salvar o create_date e o alter_date pq o model já faz isso. tirar de todos os lugares
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
            folder = kwargs['folder']
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


class PersonListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Person
    table_class = PersonTable


class PersonCreateView(LoginRequiredMixin, SuccessMessageMixin, BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = new_success

    def form_valid(self, form):

        user = User.objects.get(id=self.request.user.id)

        if form.instance.id is None:
            form.instance.create_user = user
        else:
            form.instance.alter_user = user

        legal_type = self.request.POST['legal_type']
        cnpj = self.request.POST['cnpj']
        cpf = self.request.POST['cpf']

        if legal_type is 'F' and cpf:
            form.instance.cpf_cnpj = cpf
        elif legal_type is 'J' and cnpj:
            form.instance.cpf_cnpj = cnpj
        form.save()

        super(PersonCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)


class PersonUpdateView(LoginRequiredMixin, BaseCustomView, SuccessMessageMixin, UpdateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = update_success

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     context = self.get_context_data(object=self.object)
    #     return self.render_to_response(context)

    def form_valid(self, form):
        legal_type = self.request.POST['legal_type']
        cnpj = self.request.POST['cnpj']
        cpf = self.request.POST['cpf']

        if legal_type is 'F' and cpf:
            form.instance.cpf_cnpj = cpf
        elif legal_type is 'J' and cnpj:
            form.instance.cpf_cnpj = cnpj
        form.save()

        return super(PersonUpdateView, self).form_valid(form)


class PersonDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = Person
    success_url = reverse_lazy('person_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()
        testee = self.request.user.is_authenticated()
        qs = Person.objects.none()

        if self.q:
            qs = Person.objects.filter(legal_name__istartswith=str(self.q), is_active=True, is_customer=True)

        return qs


class GenericFormOneToMany(FormView, SingleTableView):
    def get_initial(self):

        if isinstance(self, CreateView):
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True

        elif isinstance(self, UpdateView):
            self.form_class.declared_fields['is_active'].disabled = False
        return self.initial.copy()

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)

        if form.instance.id is None:
            # todo: nao precisa salvar o create_date e o alter_date pq o model já faz isso. tirar de todos os lugares
            form.instance.create_date = timezone.now()
            form.instance.create_user = user
        else:

            form.instance.alter_date = timezone.now()
            form.instance.alter_user = user
            form.save()
        super(GenericFormOneToMany, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    success_message = None
