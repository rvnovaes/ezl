import importlib
import json
from abc import abstractproperty
from functools import wraps
from django import forms
from django.forms.utils import ErrorList
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import ProtectedError, Q, F
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View
from django.views import View
from django.views.generic import ListView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from allauth.account.views import LoginView, PasswordResetView
from dal import autocomplete
from django_tables2 import SingleTableView, RequestConfig

from core.forms import PersonForm, AddressForm, UserUpdateForm, UserCreateForm, ResetPasswordFormMixin, AddressFormSet, AddressOfficeFormSet, OfficeForm
from core.generic_search import GenericSearchForeignKey, GenericSearchFormat, \
    set_search_model_attrs
from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, delete_error_protected, \
    record_from_wrong_office, DELETE_SUCCESS_MESSAGE, \
    ADDRESS_UPDATE_ERROR_MESSAGE, \
    ADDRESS_UPDATE_SUCCESS_MESSAGE
from core.models import Person, Address, City, State, Country, AddressType, Office, Invite, DefaultOffice
from core.signals import create_person
from core.tables import PersonTable, UserTable, AddressTable, AddressOfficeTable, OfficeTable
from core.utils import login_log, logout_log, get_office_session
from financial.models import ServicePriceTable
from lawsuit.models import Folder, Movement, LawSuit, Organ
from task.models import Task
from ecm.forms import AttachmentForm

class AutoCompleteView(autocomplete.Select2QuerySetView):
    model = abstractproperty()
    lookups = abstractproperty()
    select_related = None

    @classmethod
    def get_part_queryset(cls, part, queryset):
        q = Q()
        for lookup in cls.lookups:
            q |= Q(**{lookup: part})

        return queryset.filter(q)

    def get_queryset(self):
        if self.select_related:
            qs = self.model.objects.select_related(*self.select_related)

        if self.q:
            parts = self.q.split(' ')

            for part in parts:
                qs = self.get_part_queryset(part, qs)
                if not qs.exists():
                    return self.model.objects.none()

            return qs

        else:
            qs = qs[:10]

        return qs


class CityAutoCompleteView(AutoCompleteView):
    model = City
    lookups = (
        'name__unaccent__icontains',
        'state__initials__exact',
        'state__name__unaccent__contains',
        'state__country__name__unaccent__contains',
    )
    select_related = ('state__country', 'state', )

    def get_result_label(self, result):
        return '{} - {}/{} - {}'.format(result.name,
                                        result.state.initials,
                                        result.state.name,
                                        result.state.country.name)


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('dashboard'))
    else:
        return render(request, 'account/login.html')


@login_required
def inicial(request):
    if request.user.is_authenticated:
        if request.user.person.offices.all().exists():
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        return HttpResponseRedirect(reverse_lazy('start_user'))
    else:
        return HttpResponseRedirect('/')

class StartUserView(View):
    template_name = 'core/start_user.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


@logout_log
def logout_user(request):
    # Faz o logout do usuário contido na requisição, limpando todos os dados da sessão corrente;
    logout(request)
    # Redireciona para a página de login
    return HttpResponseRedirect('/')


class MultiDeleteViewMixin(DeleteView):
    success_message = None

    def delete(self, request, *args, **kwargs):
        if request.method == 'POST':
            pks = request.POST.getlist('selection')

            try:
                self.model.objects.filter(pk__in=pks).delete()
                messages.success(self.request, self.success_message)
            except ProtectedError as e:
                qs = e.protected_objects.first()
                # type = type('Task')
                messages.error(self.request,
                               delete_error_protected(str(self.model._meta.verbose_name),
                                                      qs.__str__()))

        # http://django-tables2.readthedocs.io/en/latest/pages/generic-mixins.html
        if self.success_url:
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(self.get_success_url())


def remove_invalid_registry(f):
    """
    Embrulha o metodo get_context_data onde deseja remover da listagem  o registro invalido gerado
    pela ETL.
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


class LoginCustomView(LoginView):
    """
    Esta classe herda da view que e responsavel por realizar o login no django-allauth
    """

    @login_log
    def form_valid(self, form):
        """
        Este metodo valida o formulario de login e faz a chamada da funcao que
        efetuar a autenticacao
        Esta sendo sobrescrito para gerar o log de autenticacao de usuario atraves
        do decorator log
        :param form:
        """
        return super(LoginCustomView, self).form_valid(form)


class AuditFormMixin(LoginRequiredMixin, SuccessMessageMixin):
    """
    Implementa a alteração da data e usuários para operação de update e new
    Lógica que verifica se a requisição é para Create ou Update.
    Se Create, o botão 'ativar' é desabilitar e valor padrão True
    Se Update, o botão 'ativar é habilitado para edição e o valor, carregado do banco
    """

    object_list_url = None

    def get_context_data(self, **kwargs):
        kwargs.update({'form_attachment': AttachmentForm})
        return super().get_context_data(object_list_url=self.get_object_list_url(), **kwargs)

    def get_object_list_url(self):
        if self.object_list_url:
            return reverse(self.object_list_url)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'is_active' in form.fields and not form.instance.pk:
            form.data = form.data.copy()
            form.data['is_active'] = True
            form.fields['is_active'].initial = True
            form.fields['is_active'].required = False
            form.fields['is_active'].widget.attrs['disabled'] = 'disabled'
        return form

    def form_valid(self, form):
        instance = form.save(commit=False)

        if 'is_active' in form.fields and not instance.pk:
            instance.is_active = True

        if form.instance.id is None:
            form.instance.create_date = timezone.now()
            form.instance.create_user = self.request.user
        else:
            form.instance.alter_date = timezone.now()
            form.instance.alter_user = self.request.user
            form.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class AddressMixin(AuditFormMixin):
    def __init__(self, related_model=None, related_field_pk=False, related_model_name=''):
        self.related_model = related_model
        self.related_model_name = related_model_name
        self.related_field_pk = related_field_pk
        self.object_related = None

    def dispatch(self, *args, **kwargs):
        self.object_related = self.related_model.objects.get(
            pk=kwargs['{}_pk'.format(self.related_field_pk)])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(person=self.object_related, **kwargs)

    def form_valid(self, form):
        form.save(commit=False)
        setattr(form.instance, self.related_model_name, self.object_related)
        return super().form_valid(form)

    def get_object_list_url(self):
        # TODO: Este método parece ser inútil, success_url pode ser usado.
        return reverse('{}_update'.format(self.related_model_name), args=(self.object_related.pk, ))


class AddressCreateView(AddressMixin, CreateView):
    model = Address
    form_class = AddressForm
    success_message = CREATE_SUCCESS_MESSAGE

    def __init__(self):
        super().__init__(related_model=Person, related_model_name='person',
                         related_field_pk='person')

    def get_success_url(self):
        return reverse('person_update', args=(self.object.person.pk, ))


class AddressOfficeCreateView(AddressMixin, CreateView):
    model = Address
    form_class = AddressForm
    success_message = CREATE_SUCCESS_MESSAGE

    def __init__(self):
        super().__init__(related_model=Office, related_model_name='office',
                         related_field_pk='office')

    def get_success_url(self):
        return reverse('office_update', args=(self.object.office.pk, ))


class AddressUpdateView(AddressMixin, UpdateView):
    model = Address
    form_class = AddressForm
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_success_url(self):
        return reverse('person_update', args=(self.object.person.pk, ))

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get('person_pk'):
            obj = Person.objects.get(id=self.kwargs.get('person_pk'))
        office_session = get_office_session(request=request)
        if obj.offices.filter(pk=office_session.pk).first() != office_session:
            messages.error(self.request, record_from_wrong_office(), )
            return HttpResponseRedirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)


class AddressDeleteView(AddressMixin, MultiDeleteViewMixin):
    model = Address
    form_class = AddressForm
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)

    def get_success_url(self):
        return reverse('person_update', kwargs={'pk': self.kwargs['person_pk']})


class SingleTableViewMixin(SingleTableView):
    ordering = None
    paginate_by = 10

    @classmethod
    def filter_queryset(cls, queryset):
        if cls.ordering:
            return queryset.order_by(*cls.ordering)
        else:
            return queryset

    @set_search_model_attrs
    def get_context_data(self, **kwargs):
        context = super(SingleTableViewMixin, self).get_context_data(**kwargs)
        context['module'] = self.model.__module__
        context['model'] = self.model.__name__
        try:
            context['nav_' + str(self.model._meta.verbose_name)] = True
        except:
            pass
        context['form_name'] = self.model._meta.verbose_name
        context['form_name_plural'] = self.model._meta.verbose_name_plural
        context['page_title'] = self.model._meta.verbose_name_plural

        custom_session_user = self.request.session.get('custom_session_user')
        office = False
        if custom_session_user and custom_session_user.get(str(self.request.user.pk)):
            current_office_session = custom_session_user.get(str(self.request.user.pk))
            office = Office.objects.filter(pk=int(current_office_session.get(
                'current_office'))).values_list('id', flat=True)
        if not office:
            office = self.request.user.person.offices.all().values_list('id', flat=True)

        generic_search = GenericSearchFormat(self.request, self.model, self.model._meta.fields)
        args = generic_search.despatch(office=office)
        if args:
            table = eval(args)
        else:
            qs = self.model.objects.get_queryset()
            try:
                office_field = self.model._meta.get_field('office')
                if office:
                    qs = self.model.objects.get_queryset(office=office)
            except:
                pass
            if kwargs.get('remove_invalid'):
                qs = self.filter_queryset(
                    qs.filter(~Q(pk=kwargs.get('remove_invalid'))))
                table = self.table_class(qs)
            else:
                qs = self.filter_queryset(qs)
                table = self.table_class(qs)
        total_colums = len(table.columns.items())
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(table)
        context['table'] = table
        context['total_columns'] = total_colums
        return context


def address_update(request, pk):
    instance = get_object_or_404(Address, id=pk)
    form = AddressForm(request.POST or None, instance=instance)

    # Todo: Trocar o codigo de data por serialize()
    data = {
        'result': False,
        'message': ADDRESS_UPDATE_ERROR_MESSAGE,
        'city': str(form.instance.city),
        'state': str(form.instance.state),
        'country': str(form.instance.country),
        'address_type': str(form.instance.address_type)

    }

    if form.is_valid():
        form.save()
        data = {
            'result': True,
            'message': ADDRESS_UPDATE_SUCCESS_MESSAGE
        }

    return JsonResponse(data)


class PersonListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Person
    table_class = PersonTable
    ordering = ('legal_name', 'name', )


    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator remove_invalid_registry
        para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        context = super(PersonListView, self).get_context_data(**kwargs)
        office_session = get_office_session(request=self.request)
        table = self.table_class(
            context['table'].data.data.filter(offices=office_session).exclude(pk__in=Organ.objects.all()).order_by('-pk'))
        context['table'] = table
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        return context


class PersonCreateView(AuditFormMixin, CreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')

    def get_context_data(self, **kwargs):
        data = super(PersonCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['personaddress'] = AddressFormSet(self.request.POST)
        else:
            data['personaddress'] = AddressFormSet()
            data['personaddress'].forms[0].fields['is_active'].initial = True
            data['personaddress'].forms[0].fields['is_active'].widget.attrs['class'] = 'filled-in'
        return data

    def form_valid(self, form):

        if AuditFormMixin.form_valid(self, form):
            context = self.get_context_data()
            personaddress = context['personaddress']
            with transaction.atomic():
                self.object = form.save(commit=False)
                office_session = get_office_session(self.request)
                if self.object.cpf_cnpj is not None and\
                        office_session.persons.filter(cpf_cnpj=self.object.cpf_cnpj).first():
                    form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                        u'Já existe uma pessoa cadastrada com este CPF/CNPJ para este escritório'
                    ])
                    return self.form_invalid(form)

                self.object = form.save()
                self.object.offices.add(office_session)

                if personaddress.is_valid():
                    address = personaddress.forms[0].save(commit=False)
                    address.person = self.object
                    address.create_user = self.request.user
                    address.save()
            return super(PersonCreateView, self).form_valid(form)


class PersonUpdateView(AuditFormMixin, UpdateView):
    model = Person
    form_class = PersonForm
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'person_list'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'table': AddressTable(self.object.address_set.all()),
        })
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        user = User.objects.get(id=self.request.user.id)
        kw['is_superuser'] = user.is_superuser
        return kw

    def get_success_url(self):
        return reverse('person_update', args=(self.object.id,))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        office_session = get_office_session(request=request)
        if obj.offices.filter(pk=office_session.pk).first() != office_session:
            messages.error(self.request, record_from_wrong_office(), )

            return HttpResponseRedirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)


class PersonDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = Person
    success_url = reverse_lazy('person_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)
    object_list_url = 'person_list'


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()

        qs = Person.objects.none()
        office = self.forwarded.get('office', None)

        if self.q:
            qs = Person.objects.filter(legal_name__unaccent__istartswith=self.q,
                                       is_customer=True,
                                       offices=office)
        return qs


class CorrespondentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Person.objects.none()

        if self.q:
            Person.objects.filter()
            qs = Person.objects.filter(
                legal_name__unaccent__istartswith=self.q,
                auth_user__groups__name=Person.CORRESPONDENT_GROUP
            )
        return qs


class CorrespondentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()

        qs = Person.objects.none()

        if self.q:
            qs = Person.objects.active().correspondents().filter(legal_name__unaccent__istartswith=self.q)
        return qs


class RequesterAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()

        qs = Person.objects.none()

        if self.q:
            qs = Person.objects.active().requesters().filter(legal_name__unaccent__istartswith=self.q)
        return qs


class ServiceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #     return Person.objects.none()

        qs = Person.objects.none()

        if self.q:
            qs = Person.objects.active().services().filter(legal_name__unaccent__istartswith=self.q)
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
                qs = list(filter(lambda i: i.id in ids,
                                 eval('model.{0}.get_queryset()'.format(field_name))))
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
    states_json = json.dumps({'number': len(states), 'states': list(states)},
                             cls=DjangoJSONEncoder)
    return JsonResponse(states_json, safe=False)


@login_required
def person_address_search_city(request, pk):
    cities = City.objects.filter(state_id=pk).values('name', 'id').order_by('name')
    cities_json = json.dumps({'number': len(cities), 'cities': list(cities)},
                             cls=DjangoJSONEncoder)
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
    related_ordering = None

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
            # TODO: nao precisa salvar o create_date e o alter_date pq o model já faz isso. tirar
            # de todos os lugares
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
        related_model_id = self.kwargs.get('pk')
        context['module'] = self.related_model.__module__
        context['model'] = self.related_model.__name__
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        fields_related = list(
            filter(lambda i: i.get_internal_type() == 'ForeignKey',
                   self.related_model._meta.fields))
        field_related = list(filter(lambda i: i.related_model == self.model,
                                    fields_related))[0]
        generic_search = GenericSearchFormat(self.request, self.related_model,
                                             self.related_model._meta.fields,
                                             related_id=related_model_id,
                                             field_name_related=field_related.name)
        args = generic_search.despatch()
        if args:
            table = eval(args.replace('.model.', '.related_model.'))
        else:
            table = self.table_class(self.related_model.objects.none())
            if related_model_id:
                lookups = {'{}__id'.format(field_related.name): related_model_id}
                qs = self.related_model.objects.filter(**lookups)

                if self.related_ordering:
                    qs = qs.order_by(*self.related_ordering)

                table = self.table_class(qs)

        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        # table = self.table_class(self.related_model.objects.none())
        # context['table'] = table
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
    ordering = ('first_name', 'last_name', 'username', 'email', )


class UserCreateView(AuditFormMixin, CreateView):
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('user_list')
    success_message = CREATE_SUCCESS_MESSAGE

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


class UserUpdateView(AuditFormMixin, UpdateView):
    model = User

    form_class = UserUpdateForm
    success_url = reverse_lazy('user_list')
    success_message = UPDATE_SUCCESS_MESSAGE

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
            default_office = form.cleaned_data['office']

            obj = DefaultOffice.objects.filter(auth_user=form.instance).first()
            if obj:
                obj.office=default_office
                obj.alter_user=self.request.user
                obj.save()
            else:
                DefaultOffice.objects.create(auth_user=form.instance, office=default_office,
                                             create_user=self.request.user)

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

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class UserDeleteView(LoginRequiredMixin, MultiDeleteViewMixin):
    model = User
    success_url = reverse_lazy('user_list')
    success_message = DELETE_SUCCESS_MESSAGE.format('usuários')

    def get_success_url(self):
        return reverse_lazy('user_list')


class PasswordResetViewMixin(PasswordResetView, FormView):
    form_class = ResetPasswordFormMixin

    def form_valid(self, form):
        context = form.save(self.request)
        return render(self.request, 'account/password_reset_done.html', context)


class OfficeListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Office
    table_class = OfficeTable


class OfficeCreateView(AuditFormMixin, CreateView):
    model = Office
    form_class = OfficeForm
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'office_list'

    def form_valid(self, form):
        form.instance.create_user = self.request.user
        form.instance.save()
        form.instance.persons.add(form.instance.create_user.person)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('office_update', kwargs={'pk': self.object.pk})


class OfficeUpdateView(AuditFormMixin, UpdateView):
    model = Office
    form_class = OfficeForm
    success_url = reverse_lazy('office_list')
    template_name_suffix = '_update_form'
    success_message = UPDATE_SUCCESS_MESSAGE
    object_list_url = 'office_list'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'table': AddressOfficeTable(self.object.adresses.all()),
        })
        return super().get_context_data(**kwargs)


class OfficeDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    form_class = AddressForm
    success_message = DELETE_SUCCESS_MESSAGE.format(model._meta.verbose_name_plural)


class RegisterNewUser(CreateView):
    model = User
    fields = ('username', 'password')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        User.objects.create_user(username=username, email=email, password=password)
        # Todo: Nao esta redirecionando para o dashboard ao se cadastrar
        return login(request)


class CustomSession(View):
    def post(self, request, *args, **kwargs):
        """
        Cria uma sessao customizada do usuario para armazenar o escritorio atual
        do usuario. O Valor e armazenando na sessao atravez da chave
        custom_session_user, que ira possuir um dicionario contendo como chave
        o id do usuario e como valor um dicionario contendo o current_office.
        """
        data = {}
        if request.POST.get('current_office'):
            custom_session_user = self.request.session.get('custom_session_user')
            if not custom_session_user:
                data['modified'] = True
            elif custom_session_user.get(str(self.request.user.pk)).get('current_office') \
                    != request.POST.get('current_office'):
                data['modified'] = True
            current_office = request.POST.get('current_office')
            request.session['custom_session_user'] = {
                self.request.user.pk: {'current_office': current_office}
            }
            office = Office.objects.filter(pk=int(current_office)).first()
            if office:
                data['current_office_pk'] = office.pk
                data['current_office_name'] = office.name
            else:
                request.session.modified = True
                del request.session['custom_session_user']
                data['modified'] = True

        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        """
        Busca a sessao customizada pra do usuario que retorna informacoes
        do escritorio atual do usuario
        """
        data = {}
        custom_session_user = request.session.get('custom_session_user')
        if custom_session_user and custom_session_user.get(str(request.user.pk)):
            current_office_session = custom_session_user.get(str(request.user.pk))
            office = Office.objects.filter(pk=int(current_office_session.get(
                'current_office'))).first()
            if office:
                data['current_office_pk'] = office.pk
                data['current_office_name'] = office.name
        else:
            default_office = DefaultOffice.objects.filter(auth_user=request.user).first()
            if default_office:
                data['current_office_pk'] = default_office.office.pk
                data['current_office_name'] = default_office.office.name
        return JsonResponse(data)


class InviteCreateView(AuditFormMixin, CreateView):
    model = Invite
    success_url = reverse_lazy('start_user')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'start_user'


class InviteUpdateView(UpdateView):
    def post(self, request, *args, **kargs):
        invite = Invite.objects.get(pk=int(request.POST.get('invite_pk')))
        invite.status = request.POST.get('status')
        if invite.status == 'A':
            invite.office.persons.add(request.user.person.pk)
        invite.save()
        return HttpResponse('ok')


class EditableListSave(LoginRequiredMixin, View):
    """
    O nome da classe ficou generico pelo fato desta view poder ser utilizada
    em outras classes.
    """

    models = {"ServicePriceTable": ServicePriceTable}

    def post(self, request):
        items = json.loads(request.POST['items'])
        for item in items:
            model_class = self.models.get(item['model'])
            if model_class is None:
                continue
            instance = model_class.objects.get(id=item['id'])
            for field_item in item['fields']:
                setattr(instance, field_item['field'], field_item['value'])
            instance.save()

        return JsonResponse({"ok": True})


class ListUsersToInviteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all().values(
            'pk', 'username', 'email', 'person__name', 'person__pk')
        return JsonResponse({'data': list(users)})


class InviteMultipleUsersView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if self.request.POST.get('persons') and self.request.POST.get('office'):
            persons = self.request.POST.getlist('persons')
            office_pk = self.request.POST.get('office')
            for person_pk in persons:
                person = Person.objects.get(pk=person_pk)
                office = Office.objects.get(pk=office_pk)
                Invite.objects.create(create_user=request.user, person=person,
                                      office=office, status='N')
            return HttpResponseRedirect(reverse_lazy('office_update', kwargs={'pk': office_pk}))
        return reverse_lazy('office_list')


class TypeaHeadGenericSearch(View):
    """
    Responsavel por gerar os filtros do campo typeahead
    """
    def get(self, request, *args, **kwargs):
        module = importlib.import_module(self.request.GET.get('module'))
        model = getattr(module, self.request.GET.get('model'))
        field = request.GET.get('field')
        f = "model.objects.filter({field}__unaccent__icontains=request.GET.get('q')).annotate(value=F('{field}')).values('id', 'value')".format(field=field)
        return JsonResponse(list(eval(f)), safe=False)
