import importlib
import json
from datetime import datetime

from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.messages import storage
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_tables2 import SingleTableView, RequestConfig

from core.forms import PersonForm, AddressForm, AddressFormSet, UserUpdateForm, UserCreateForm
from core.generic_search import GenericSearchForeignKey
from core.generic_search import GenericSearchFormat
from core.generic_search import set_search_model_attrs
from core.messages import new_success, update_success, delete_error_protected, delete_success, \
    address_error_update, \
    address_success_update, duplicate_cpf, duplicate_cnpj
from core.models import Person, Address, City, State, Country, AddressType
from core.signals import create_person
from core.tables import PersonTable, UserTable
from ezl import settings
from lawsuit.models import Folder, Movement, LawSuit
from task.models import Task
from django.db.models import Q
from functools import wraps
from django.core.cache import cache


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


def remove_invalid_registry(f):
    """
    Embrulha o metodo get_context_data onde deseja remover da listagem  o registro invalido gerado pela ETL.
    :param f:
    :return f:
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            model = args[0].model
            class_verbose_name_invalid = model._meta.verbose_name.upper() + '-INVÁLIDO'
            try:
                invalid_registry = model.objects.filter(name=class_verbose_name_invalid).first()
            except:
                invalid_registry = model.objects.filter(legacy_code='REGISTRO-INVÁLIDO').first()
            if invalid_registry:
                kwargs['remove_invalid'] = invalid_registry.pk
        except:
            pass
        res = f(*args, **kwargs)
        return res
    return wrapper


# Implementa a alteração da data e usuários para operação de update e new
class BaseCustomView(FormView):
    success_url = None

    # Lógica que verifica se a requisição é para Create ou Update.
    # Se Create, o botão 'ativar' é desabilitar e valor padrão True
    # Se Update, o botão 'ativar é habilitado para edição e o valor, carregado do banco
    def get_initial(self):

        try:
            if isinstance(self, CreateView):
                self.form_class.declared_fields['is_active'].initial = True
                self.form_class.declared_fields['is_active'].disabled = True

            elif isinstance(self, UpdateView):
                self.form_class.declared_fields['is_active'].disabled = False

        except:
            pass

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
        super().form_valid(form)
        return HttpResponseRedirect(self.success_url)


class SingleTableViewMixin(SingleTableView):
    @set_search_model_attrs
    def get_context_data(self, **kwargs):
        context = super(SingleTableViewMixin, self).get_context_data(**kwargs)
        try:
            context['module'] = self.model.__module__
            context['model'] = self.model.__name__
            try:
                context['nav_' + str(self.model._meta.verbose_name)] = True
            except:
                pass
            context['form_name'] = self.model._meta.verbose_name
            context['form_name_plural'] = self.model._meta.verbose_name_plural
            generic_search = GenericSearchFormat(self.request, self.model, self.model._meta.fields)
            args = generic_search.despatch()
            if args:
                table = eval(args)
            else:
                if kwargs.get('remove_invalid'):
                    table = self.table_class(
                        self.model.objects.filter(~Q(pk=kwargs.get('remove_invalid'))).order_by('-pk'))
                else:
                    table = self.table_class(self.model.objects.all().order_by('-pk'))
            RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
            context['table'] = table
        except:
            table = self.table_class(self.model.objects.none())
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
                               delete_error_protected(str(self.model._meta.verbose_name)
                                                      , qs.__str__()))

        # http://django-tables2.readthedocs.io/en/latest/pages/generic-mixins.html
        return HttpResponseRedirect(self.success_url)


def address_update(request, pk):
    instance = get_object_or_404(Address, id=pk)
    form = AddressForm(request.POST or None, instance=instance)

    data = {
        'result': False,
        'message': address_error_update(),
        'city': str(form.instance.city),
        'state': str(form.instance.state),
        'country': str(form.instance.country),
        'address_type': str(form.instance.address_type)

    }

    if form.is_valid():
        form.save()
        data = {
            'result': True,
            'message': address_success_update()
        }

    return JsonResponse(data)


class PersonListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Person
    table_class = PersonTable

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator remove_invalid_registry
        para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        return super(PersonListView, self).get_context_data(**kwargs)


class PersonCreateView(LoginRequiredMixin, SuccessMessageMixin, BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = new_success
    addresses_form = AddressForm()

    def form_valid(self, form):

        user = User.objects.get(id=self.request.user.id)

        if form.instance.id is None:
            form.instance.create_user = user
        else:
            form.instance.alter_user = user

        person_form = PersonForm(self.request.POST)
        legal_type = self.request.POST['legal_type']
        cnpj = self.request.POST['cnpj']
        cpf = self.request.POST['cpf']

        message = 'CPF/CNPJ já existente'

        if legal_type is 'F' and cpf:
            person_form.instance.cpf_cnpj = cpf
            message = duplicate_cpf(None)
        elif legal_type is 'J' and cnpj:
            person_form.instance.cpf_cnpj = cnpj
            message = duplicate_cnpj(cnpj)

        if person_form.is_valid():
            person_form.instance.create_date = datetime.now()
            person_form.instance.create_user = User.objects.get(id=self.request.user.id)

            try:
                person = person_form.save()

            except IntegrityError:
                messages.error(self.request, message)
                context = self.get_context_data()
                return render(self.request, 'core/person_form.html', context)

            addresses_form = AddressFormSet(self.request.POST, instance=Person.objects.get(id=person.id))

            if addresses_form.is_valid():
                for address in addresses_form:

                    if address.cleaned_data['id']:
                        id_form = address.cleaned_data['id'].id
                        pass

                    else:
                        address.instance.create_date = datetime.now()
                        address.instance.create_user = User.objects.get(id=self.request.user.id)
                        address.save()
                messages.success(self.request, self.success_message)

            else:
                for error in addresses_form.errors:
                    messages.error(self.request, error)

                return HttpResponseRedirect(self.success_url)

            messages.success(self.request, self.success_message)

        # super(PersonCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(PersonCreateView, self).get_context_data(**kwargs)
        context['form_address'] = AddressForm()
        context['has_person'] = False
        # context['address_formset'] = AddressFormSet()

        if self.request.POST:
            address_formset = AddressFormSet(self.request.POST)
            context['addresses'] = address_formset.cleaned_data

        else:
            context['formset'] = AddressFormSet()
        return context


class PersonUpdateView(LoginRequiredMixin, SuccessMessageMixin, BaseCustomView, UpdateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = update_success

    def form_invalid(self, form):

        messages.error(self.request, form.errors)
        return super(PersonUpdateView, self).form_invalid(form)

    def form_valid(self, form):

        legal_type = self.request.POST['legal_type']
        cnpj = self.request.POST['cnpj']
        cpf = self.request.POST['cpf']

        message = 'CPF/CNPJ já existente'
        if legal_type is 'F' and cpf:
            form.instance.cpf_cnpj = cpf
            message = duplicate_cpf(cpf)

        elif legal_type is 'J' and cnpj:
            form.instance.cpf_cnpj = cnpj
            message = duplicate_cnpj(cnpj)

        try:
            form.save()

        except IntegrityError:
            messages.error(self.request, message)
            context = self.get_context_data()
            return HttpResponseRedirect(self.request.environ.get('PATH_INFO'))

        return super(PersonUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(person=self.object.id)
        context['form_address'] = AddressForm()
        context['address_formset'] = AddressFormSet()
        cache.set('person_page', self.request.META.get('HTTP_REFERER'))
        return context

    def post(self, request, *args, **kwargs):
        if cache.get('person_page'):
            self.success_url = cache.get('person_page')
        res = super(PersonUpdateView, self).post(request, *args, **kwargs)
        addresses_form = AddressFormSet(self.request.POST,
                                        instance=Person.objects.get(id=kwargs['pk']))

        if addresses_form.is_valid():
            for address in addresses_form:
                # Form foi marcado para deleção
                if address.cleaned_data['DELETE'] and self.request.POST['is_delete'] == '3':
                    Address.objects.get(id=address.cleaned_data['id'].id).delete()
                    messages.success(request, "Registro(s) excluído(s) com sucesso")

                # Endereço já existe no banco
                elif address.cleaned_data['id']:
                    a = Address.objects.get(id=address.cleaned_data['id'].id)
                    a.street = address.instance.street
                    a.number = address.instance.number
                    a.complement = address.instance.complement
                    a.city_region = address.instance.city_region
                    a.country = address.instance.country
                    a.state = address.instance.state
                    a.city = address.instance.city
                    a.notes = address.instance.notes
                    a.address_type = address.instance.address_type
                    a.zip_code = address.instance.zip_code

                    if address.cleaned_data['is_active'] is True or address.cleaned_data['is_active'] is 'on':
                        a.is_active = True
                    else:
                        a.is_active = False

                    # a.is_active = address.instance.is_active

                    a.save(
                        update_fields=['street', 'number', 'complement', 'city_region', 'country',
                                       'state', 'city',
                                       'notes', 'address_type', 'zip_code', 'is_active'])

                # Endereço não existe no banco (novo endereço) e será salvo
                else:
                    address.instance.create_date = datetime.now()
                    address.instance.create_user = User.objects.get(id=self.request.user.id)
                    address.save()
        else:
            for error in addresses_form.errors:
                messages.error(self.request, error)
        return res


class PersonDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = Person
    success_url = reverse_lazy('person_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()

        qs = Person.objects.none()

        if self.q:
            qs = Person.objects.filter(legal_name__unaccent__istartswith=self.q, is_customer=True)
        return qs


class GenericAutocompleteForeignKey(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        try:
            module = importlib.import_module(self.request.GET.get('module'))
            model = getattr(module, self.request.GET.get('model'))
            field_name = self.request.GET.get('name')
            qs = model.objects.none()
            if self.q:
                generic_search = GenericSearchForeignKey(model)
                ids = generic_search.get_related_values(self.q, field_name)
                qs = list(filter(lambda i: i.id in ids, eval('model.{0}.get_queryset()'.format(field_name))))
            return qs
        except:
            return []


@login_required
def person_address_search_country(request):
    countries = Country.objects.filter(id__gt=1).values('name', 'id').order_by('name')
    countries_json = json.dumps({'number': len(countries), 'countries': list(countries)},
                                cls=DjangoJSONEncoder)
    return JsonResponse(countries_json, safe=False)


@login_required
def person_address_search_state(request, pk):
    states = State.objects.filter(country_id=pk).values('name', 'id').order_by('name')
    states_json = json.dumps({'number': len(states), 'states': list(states)}, cls=DjangoJSONEncoder)
    return JsonResponse(states_json, safe=False)


@login_required
def person_address_search_city(request, pk):
    cities = City.objects.filter(state_id=pk).values('name', 'id').order_by('name')
    cities_json = json.dumps({'number': len(cities), 'cities': list(cities)}, cls=DjangoJSONEncoder)
    return JsonResponse(cities_json, safe=False)


@login_required
def person_address_information(request, pk):
    try:
        address = Address.objects.get(id=pk)
        data = {
            'result': True,
            'street': address.street,
            'number': address.number,
            'complement': address.complement,
            'city_region': address.city_region,
            'state_id': str(address.state_id),
            'state': str(address.state),
            'city': str(address.city),
            'city_id': str(address.city_id),
            'address_type': str(address.address_type),
            'address_type_id': str(address.address_type_id),
            'zip_code': address.zip_code,
            'notes': address.notes,
            'home_address': address.home_address,
            'business_address': address.business_address,
            'country': str(address.country),
            'country_id': str(address.country_id),
            'person': str(address.person_id),
            'is_active': address.is_active
        }
    except:
        data = {
            'result': False
        }

    return JsonResponse(data)


@login_required
def person_address_search_address_type(request):
    addresses_types = AddressType.objects.all().values('name', 'id')
    addresses_types_json = json.dumps(
        {'number': len(addresses_types), 'addresses_types': list(addresses_types)},
        cls=DjangoJSONEncoder)
    return JsonResponse(addresses_types_json, safe=False)


class GenericFormOneToMany(FormView, SingleTableView):
    def get_initial(self):
        if self.kwargs.get('lawsuit'):
            folder_id = LawSuit.objects.get(id=self.kwargs.get('lawsuit')).folder.id
            self.kwargs['folder'] = folder_id
        if isinstance(self, CreateView):
            self.form_class.declared_fields['is_active'].initial = True
            self.form_class.declared_fields['is_active'].disabled = True

        elif isinstance(self, UpdateView):
            self.form_class.declared_fields['is_active'].disabled = False
        return self.initial.copy()

    def form_valid(self, form):
        user = User.objects.get(id=self.request.user.id)
        folder = self.kwargs.get('folder') or None
        lawsuit = self.kwargs.get('lawsuit') or None
        movement = self.kwargs.get('movement') or None
        pk = self.kwargs.get('pk')
        if form.instance.id is None:
            if folder:
                form.instance.folder = Folder.objects.get(id=folder)
                if isinstance(self, UpdateView):
                    form.instance.law_suit = LawSuit.objects.get(id=pk)
            if lawsuit:
                form.instance.law_suit = LawSuit.objects.get(id=lawsuit)
                if isinstance(self, UpdateView):
                    form.instance.movement = Movement.objects.get(id=pk)
            if movement:
                form.instance.movement = Movement.objects.get(id=movement)
                if isinstance(self, UpdateView):
                    form.instance.task = Task.objects.get(id=pk)

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

    @set_search_model_attrs
    def get_context_data(self, **kwargs):
        context = super(GenericFormOneToMany, self).get_context_data(**kwargs)
        try:
            related_model_id = self.kwargs.get('pk')
            context['module'] = self.related_model.__module__
            context['model'] = self.related_model.__name__
            context['nav_' + self.related_model._meta.verbose_name] = True
            context['form_name'] = self.related_model._meta.verbose_name
            context['form_name_plural'] = self.related_model._meta.verbose_name_plural
            fields_related = list(
                filter(lambda i: i.get_internal_type() == 'ForeignKey', self.related_model._meta.fields))
            field_related = list(filter(lambda i: i.related_model == self.model, fields_related))[0]
            generic_search = GenericSearchFormat(self.request, self.related_model, self.related_model._meta.fields,
                                                 related_id=related_model_id, field_name_related=field_related.name)
            args = generic_search.despatch()
            if args:
                table = eval(args.replace('.model.', '.related_model.'))
            else:
                table = self.table_class(self.related_model.objects.none())
                if related_model_id:
                    table_class = 'self.table_class(self.related_model.objects.filter({0}__id=related_model_id).order_by("-pk"))'.format(
                        field_related.name)
                    table = eval(table_class)
            RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
            context['table'] = table
        except:
            table = self.table_class(self.related_model.objects.none())
        context['table'] = table
        return context

    success_message = None


def recover_database(request):
    return render(request, 'core/recover_database.html',
                  {'request': False,
                   'host': settings.LINK_TO_RESTORE_DB_DEMO,
                   'timeout': 45000
                   }
                  )


class UserListView(LoginRequiredMixin, SingleTableViewMixin):
    model = User
    table_class = UserTable
    template_name = 'auth/user_list.html'


class UserCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('user_list')
    success_message = new_success

    def get_success_url(self):
        create_person
        return reverse_lazy('user_list')

    def form_valid(self, form):
        form.save()
        if form.is_valid:
            groups = form.cleaned_data['groups']
            ids = list(group.id for group in groups)

            for group in Group.objects.filter(id__in=ids):
                group.user_set.add(form.instance)

        super(UserCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)


class UserUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = User

    form_class = UserUpdateForm
    success_url = reverse_lazy('user_list')
    success_message = update_success

    def get_initial(self):
        self.form_class.declared_fields['password'].disabled = True
        self.form_class.declared_fields['username'].disabled = True
        return self.initial.copy()

    def get_success_url(self):
        return reverse_lazy('user_list')

    def form_valid(self, form):
        form.save()
        if form.is_valid:
            groups = form.cleaned_data['groups']
            ids = list(group.id for group in groups)

            for group in Group.objects.filter(id__in=ids):
                group.user_set.add(form.instance)

        super(UserUpdateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        cache.set('user_page', self.request.META.get('HTTP_REFERER'))
        return context

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o metodo post e verifica se existe cache da ultima url
        Isso e necessario pelo fato da necessidade de retornar pra mesma paginacao
        Que o usuario se encontrava ao fazer a alteracao
        :param request:
        :param args:
        :param kwargs:
        :return: super
        """
        if cache.get('user_page'):
            self.success_url = cache.get('user_page')
        return super(UserUpdateView, self).post(request, *args, **kwargs)


class UserDeleteView(SuccessMessageMixin, LoginRequiredMixin, MultiDeleteViewMixin):
    model = User
    success_url = reverse_lazy('user_list')
    success_message = delete_success('usuários')

    def get_success_url(self):
        return reverse_lazy('user_list')
