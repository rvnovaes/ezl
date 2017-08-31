import json
import urllib.parse
from datetime import datetime

from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_tables2 import SingleTableView, RequestConfig

from core.forms import PersonForm, AddressForm, AddressFormSet
from core.messages import new_success, update_success, delete_error_protected, delete_success, \
    address_error_update, \
    address_success_update, recover_database_not_permitted, recover_database_login_incorrect
from core.models import Person, Address, City, State, Country, AddressType
from core.tables import PersonTable
from lawsuit.models import Folder, Movement, LawSuit
from task.models import Task
from core.generic_search import GenericSearchFormat
from core.generic_search import GenericSearchForeignKey
from core.generic_search import set_search_model_attrs
from django.db.models import Q
import importlib


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
        super(BaseCustomView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)


class SingleTableViewMixin(SingleTableView):
    @set_search_model_attrs
    def get_context_data(self, **kwargs):
        context = super(SingleTableViewMixin, self).get_context_data(**kwargs)
        try:
            context['module'] = self.model.__module__
            context['model'] = self.model.__name__
            context['nav_' + self.model._meta.verbose_name] = True
            context['form_name'] = self.model._meta.verbose_name
            context['form_name_plural'] = self.model._meta.verbose_name_plural
            generic_search = GenericSearchFormat(self.request, self.model, self.model._meta.fields)
            args = generic_search.despatch()
            if args:
                table = eval(args)
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
            #print (kwargs)
            #folder = kwargs['folder']
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


class PersonCreateView(LoginRequiredMixin, SuccessMessageMixin, BaseCustomView, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = new_success
    addresses_form = AddressForm(initial={'street': 'teste'})

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

        if legal_type is 'F' and cpf:
            person_form.instance.cpf_cnpj = cpf
        elif legal_type is 'J' and cnpj:
            person_form.instance.cpf_cnpj = cnpj

        if person_form.is_valid():
            person_form.instance.create_date = datetime.now()
            person_form.instance.create_user = User.objects.get(id=self.request.user.id)
            person = person_form.save()
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

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_invalid(self, form):

        messages.error(self.request, form.errors)
        return super(PersonUpdateView, self).form_invalid(form)
        # context = self.get_context_data()
        # context['person'].cpf_cnpj = '111.111.111-11'
        # context['object'].cpf_cnpj = '111.111.111-11'
        # form.cleaned_data['cpf_cnpj'] = '111.111.111-11'


        # return HttpResponseRedirect(self.request.path)

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

    # def get_context_data(self, **kwargs):
    #
    #     context = super(PersonUpdateView, self).get_context_data(**kwargs)
    #     context['addresses'] = Address.objects.filter(person=self.object.id)
    #     context['form_address'] = AddressForm()
    #     context['address_formset'] = AddressFormSet()
    #
    #     return context

    def post(self, request, *args, **kwargs):
        super(PersonUpdateView, self).post(request, *args, **kwargs)
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
        return HttpResponseRedirect(self.request.path)


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
            qs = Person.objects.filter(name__unaccent__istartswith=self.q, is_customer=True)
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
    if request.POST:
        login = request.POST['login']
        password = request.POST['password']

        user = authenticate(username=login, password=password)

        if user:
            if user.is_superuser:

                context = {
                    'host': 'http://13.68.213.60:8001',
                    'request': True
                }
                return render(request, 'core/recover_database.html', context)

            elif not user.is_superuser:
                messages.error(request, recover_database_not_permitted())
                return render(request, 'core/recover_database.html', {'request': False})
        else:
            messages.error(request, recover_database_login_incorrect())
            return render(request, 'core/recover_database.html', {'request': False})

    else:
        return render(request, 'core/recover_database.html', {'request': False})
