from compat import JsonResponse
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django_tables2 import SingleTableView, RequestConfig
from datetime import datetime
from core.forms import PersonForm, AddressForm, AddressFormSet
from core.messages import new_success, update_success, delete_error_protected, delete_success, address_sucess_deleted, \
    address_error_deleted, address_success_create, address_error_create, address_error_update, address_success_update, \
    address_and_person_created, address_and_person_not_created
from core.models import Person, Address, City, State, Country, AddressType
from core.tables import PersonTable
import json
from django.core.serializers.json import DjangoJSONEncoder


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

    # def post(self, request, *args, **kwargs):
    #
    #     person_form = PersonForm(request.POST)
    #
    #     if person_form.is_valid():
    #         person_form.instance.create_date = datetime.now()
    #         person_form.instance.create_user = User.objects.get(id=self.request.user.id)
    #         person = person_form.save()
    #         addresses_form = AddressFormSet(self.request.POST, instance=Person.objects.get(id=person.id))
    #
    #         if addresses_form.is_valid():
    #             for address in addresses_form:
    #
    #                 if address.cleaned_data['id']:
    #                     id_form = address.cleaned_data['id'].id
    #                     pass
    #
    #                 else:
    #                     address.instance.create_date = datetime.now()
    #                     address.instance.create_user = User.objects.get(id=self.request.user.id)
    #                     address.save()
    #             messages.success(self.request, self.success_message)
    #
    #         else:
    #             for error in addresses_form.errors:
    #                 messages.error(request, error)
    #
    #             return HttpResponseRedirect(self.success_url)
    #
    #         messages.success(request, self.success_message)
    #         super(PersonCreateView, self).post(request, *args, **kwargs)
    #         return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(PersonCreateView, self).get_context_data(**kwargs)
        context['form_address'] = AddressForm
        context['has_person'] = False
        context['address_formset'] = AddressFormSet()

        if self.request.POST:
            context['formset'] = AddressFormSet(self.request.POST)

        else:
            context['formset'] = AddressFormSet()
        return context


class PersonUpdateView(LoginRequiredMixin, SuccessMessageMixin, BaseCustomView, UpdateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('person_list')
    success_message = update_success

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

    def get_context_data(self, **kwargs):
        context = super(PersonUpdateView, self).get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(person=self.object.id)
        context['form_address'] = AddressForm()
        context['address_formset'] = AddressFormSet()
        return context

    def post(self, request, *args, **kwargs):
        super(PersonUpdateView, self).post(request, *args, **kwargs)
        addresses_form = AddressFormSet(self.request.POST, instance=Person.objects.get(id=kwargs['pk']))

        if addresses_form.is_valid():
            for address in addresses_form:

                # Form foi marcado para deleção
                if address.cleaned_data['DELETE']:
                    Address.objects.get(id=address.cleaned_data['id'].id).delete()

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
                    a.is_active = address.instance.is_active

                    a.save(update_fields=['street', 'number', 'complement', 'city_region', 'country', 'state', 'city',
                                          'notes', 'address_type', 'zip_code', 'is_active'])

                # Endereço não existe no banco (novo endereço) e será salvo
                else:
                    address.instance.create_date = datetime.now()
                    address.instance.create_user = User.objects.get(id=self.request.user.id)
                    address.save()

        return super(PersonUpdateView, self).post(request, *args, **kwargs)


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
            qs = Person.objects.filter(name__istartswith=self.q, is_customer=True)

        return qs


@login_required
def person_address_search_country(request):
    countries = Country.objects.filter(id__gt=1).values('name', 'id')
    countries_json = json.dumps({'number': len(countries), 'countries': list(countries)}, cls=DjangoJSONEncoder)
    return JsonResponse(countries_json, safe=False)


@login_required
def person_address_search_state(request, pk):
    states = State.objects.filter(country_id=pk).values('name', 'id')
    states_json = json.dumps({'number': len(states), 'states': list(states)}, cls=DjangoJSONEncoder)
    return JsonResponse(states_json, safe=False)


@login_required
def person_address_search_city(request, pk):
    cities = City.objects.filter(state_id=pk).values('name', 'id')
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
