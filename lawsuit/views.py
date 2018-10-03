from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.validators import ValidationError
# project imports
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_tables2 import RequestConfig
from core.messages import CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE, DELETE_SUCCESS_MESSAGE, \
    delete_error_protected
from core.views import AuditFormMixin, MultiDeleteViewMixin, SingleTableViewMixin, \
    GenericFormOneToMany, AddressCreateView, AddressUpdateView, AddressDeleteView
from task.models import Task
from task.tables import TaskTable
from .forms import (TypeMovementForm, InstanceForm, MovementForm, FolderForm, LawSuitForm, CourtDistrictForm, OrganForm,
                    CourtDivisionForm, CourtDistrictComplementForm)
from .models import (Instance, Movement, LawSuit, Folder, CourtDistrict, CourtDivision, TypeMovement, Organ,
                     CourtDistrictComplement)
from .tables import (MovementTable, FolderTable, LawSuitTable, CourtDistrictTable, InstanceTable, CourtDivisionTable,
                     TypeMovementTable, OrganTable, AddressOrganTable, CourtDistrictComplementTable)
from core.views import remove_invalid_registry, PopupMixin
from django.core.cache import cache
from dal import autocomplete
from django.db.models import Q

from core.views import CustomLoginRequiredView, TypeaHeadGenericSearch


class InstanceListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = Instance
    table_class = InstanceTable

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        ret = super(InstanceListView, self).get_context_data(**kwargs)
        return ret


class InstanceCreateView(AuditFormMixin, CreateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class InstanceUpdateView(AuditFormMixin, UpdateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super(InstanceUpdateView, self).get_context_data(**kwargs)
        cache.set('instance_page', self.request.META.get('HTTP_REFERER'))
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
        if cache.get('instance_page'):
            self.success_url = cache.get('instance_page')
        return super(InstanceUpdateView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class InstanceDeleteView(SuccessMessageMixin, CustomLoginRequiredView,
                         MultiDeleteViewMixin):
    model = Instance
    success_url = reverse_lazy('instance_list')
    success_message = DELETE_SUCCESS_MESSAGE.format('instâncias')


class TypeMovementListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = TypeMovement
    table_class = TypeMovementTable


class TypeMovementCreateView(AuditFormMixin, CreateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class TypeMovementUpdateView(AuditFormMixin, UpdateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super(TypeMovementUpdateView,
                        self).get_context_data(**kwargs)
        cache.set('type_movement_page', self.request.META.get('HTTP_REFERER'))
        return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

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
        if cache.get('type_movement_page'):
            self.success_url = cache.get('type_movement_page')
        return super(TypeMovementUpdateView, self).post(
            request, *args, **kwargs)


class TypeMovementDeleteView(CustomLoginRequiredView, MultiDeleteViewMixin):
    model = TypeMovement
    success_url = reverse_lazy('type_movement_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class FolderListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = Folder
    table_class = FolderTable

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator remove_invalid_registry
        para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        return super(FolderListView, self).get_context_data(**kwargs)


class FolderCreateView(AuditFormMixin, CreateView):
    model = Folder

    form_class = FolderForm
    success_url = reverse_lazy('folder_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class FolderUpdateView(AuditFormMixin, UpdateView):
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folder_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class FolderDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = Folder
    success_url = reverse_lazy('folder_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class CourtDistrictListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = CourtDistrict
    table_class = CourtDistrictTable

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator remove_invalid_registry
        para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        return super(CourtDistrictListView, self).get_context_data(**kwargs)


class CourtDistrictCreateView(AuditFormMixin, CreateView):
    model = CourtDistrict
    form_class = CourtDistrictForm
    success_url = reverse_lazy('courtdistrict_list')
    success_message = CREATE_SUCCESS_MESSAGE


class CourtDistrictUpdateView(AuditFormMixin, UpdateView):
    model = CourtDistrict
    form_class = CourtDistrictForm
    success_url = reverse_lazy('courtdistrict_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super(CourtDistrictUpdateView,
                        self).get_context_data(**kwargs)
        cache.set('court_district_page', self.request.META.get('HTTP_REFERER'))
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
        if cache.get('court_district_page'):
            self.success_url = cache.get('court_district_page')
        return super(CourtDistrictUpdateView, self).post(
            request, *args, **kwargs)


class CourtDistrictDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = CourtDistrict
    success_url = reverse_lazy('courtdistrict_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class CourtDivisionListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = CourtDivision
    table_class = CourtDivisionTable

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator remove_invalid_registry
        para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listatem
        :rtype: dict
        """
        return super(CourtDivisionListView, self).get_context_data(**kwargs)


class CourtDivisionCreateView(AuditFormMixin, CreateView):
    model = CourtDivision
    form_class = CourtDivisionForm
    success_url = reverse_lazy('courtdivision_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CourtDivisionUpdateView(AuditFormMixin, UpdateView):
    model = CourtDivision
    form_class = CourtDivisionForm
    success_url = reverse_lazy('courtdivision_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CourtDivisionDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = CourtDivision
    success_url = reverse_lazy('courtdivision_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class FolderLawsuitCreateView(PopupMixin, AuditFormMixin, SuccessMessageMixin,
                              CreateView):
    model = Folder
    related_model = LawSuit
    form_class = FolderForm
    table_class = LawSuitTable
    template_name = 'lawsuit/folder_lawsuit_form.html'
    success_url = reverse_lazy('folder_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        context = super(FolderLawsuitCreateView,
                        self).get_context_data(**kwargs)
        context["is_popup"] = self.is_popup
        if "context" in context:
            RequestConfig(
                self.request, paginate={
                    'per_page': 10
                }).configure(context['table'])
        return context

    # TODO - verificar opção de cadastro de processos ao incluir pasta
    # def get_context_data(self, **kwargs):
    #     context = super(FolderLawsuitCreateView, self).get_context_data(**kwargs)
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(context['table'])
    #     return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def get_success_url(self):
        if self.is_popup:
            success_url = "{}?field=folder&value={}&label={}".format(
                reverse('popup_success'),
                self.object.id,
                self.object,
            )
        else:
            success_url = reverse(
                'folder_update', kwargs={"pk": self.object.id})

        self.success_url = success_url
        return success_url


class FolderLawsuitUpdateView(SuccessMessageMixin, GenericFormOneToMany,
                              UpdateView):
    model = Folder
    related_model = LawSuit
    form_class = FolderForm
    table_class = LawSuitTable
    template_name = 'lawsuit/folder_lawsuit_form.html'
    success_url = reverse_lazy('folder_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    delete_message = DELETE_SUCCESS_MESSAGE.format(
        related_model._meta.verbose_name_plural)

    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data e seta a ultima url acessada no cache
        Isso e necessario para que ao salvar uma alteracao, o metodo post consiga verificar
        a pagina da paginacao onde o usuario fez a alteracao
        :param kwargs:
        :return: super
        """
        context = super(FolderLawsuitUpdateView,
                        self).get_context_data(**kwargs)
        cache.set('folder_lawsuit_page', self.request.META.get('HTTP_REFERER'))
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
        self.object_list = []
        if cache.get('folder_lawsuit_page'):
            self.success_url = cache.get('folder_lawsuit_page')
        return super(FolderLawsuitUpdateView, self).post(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class LawSuitListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = LawSuit
    table_class = LawSuitTable


class LawSuitCreateView(AuditFormMixin, CreateView):
    model = LawSuit
    form_class = LawSuitForm
    success_message = CREATE_SUCCESS_MESSAGE

    def get_success_url(self):
        self.success_url = reverse(
            'folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawSuitCreateView, self).get_success_url()


class LawSuitUpdateView(AuditFormMixin, UpdateView):
    model = LawSuit
    form_class = LawSuitForm
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_success_url(self):
        self.success_url = reverse(
            'folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawSuitUpdateView, self).get_success_url()


class LawSuitDeleteView(AuditFormMixin, DeleteView):
    model = LawSuit
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)

    def delete(self, request, *args, **kwargs):
        pks = self.request.POST.getlist('selection')
        parent_class = self.request.POST['parent_class']
        try:
            self.model.objects.filter(pk__in=pks).delete()
            messages.success(
                self.request,
                DELETE_SUCCESS_MESSAGE.format(
                    self.model._meta.verbose_name_plural))
        except ProtectedError as e:
            qs = e.protected_objects.first()
            messages.error(
                self.request,
                delete_error_protected(self.model._meta.verbose_name,
                                       qs.__str__()))
        return HttpResponseRedirect(
            reverse('folder_update', kwargs={'pk': parent_class}))


class LawsuitMovementCreateView(PopupMixin, AuditFormMixin,
                                SuccessMessageMixin, GenericFormOneToMany,
                                CreateView):
    model = LawSuit
    related_model = Movement
    form_class = LawSuitForm
    table_class = MovementTable
    template_name = 'lawsuit/lawsuit_movement_form.html'
    success_message = CREATE_SUCCESS_MESSAGE
    object_list = []

    def get_context_data(self, **kwargs):
        context = super(LawsuitMovementCreateView,
                        self).get_context_data(**kwargs)
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context[
            'form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.none())
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get_success_url(self):
        if self.is_popup:
            self.success_url = "{}?field=lawsuit&value={}&label={}".format(
                reverse('popup_success'), self.object.id, self.object)
        else:
            self.success_url = reverse(
                'folder_update', kwargs={'pk': self.kwargs['folder']})
            super().get_success_url()

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_valid(self, form):
        try:
            res = super().form_valid(form)
        except ValidationError as e:
            form.add_error(field=None, error=e)
            return super().form_invalid(form)
        return res


class LawsuitMovementUpdateView(SuccessMessageMixin, CustomLoginRequiredView,
                                GenericFormOneToMany, UpdateView):
    model = LawSuit
    related_model = Movement
    form_class = LawSuitForm
    table_class = MovementTable
    template_name = 'lawsuit/lawsuit_movement_form.html'
    success_message = UPDATE_SUCCESS_MESSAGE
    delete_message = DELETE_SUCCESS_MESSAGE.format(
        related_model._meta.verbose_name_plural)
    object_list = []

    def get_context_data(self, **kwargs):
        context = super(LawsuitMovementUpdateView,
                        self).get_context_data(**kwargs)
        cache.set('lawsuit_movement_page',
                  self.request.META.get('HTTP_REFERER'))
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
        self.success_url = reverse(
            'folder_update', kwargs={'pk': self.kwargs['folder']})
        if cache.get('lawsuit_movement_page'):
            self.success_url = cache.get('lawsuit_movement_page')
        return super(LawsuitMovementUpdateView, self).post(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            res = super().form_valid(form)
        except ValidationError as e:
            form.add_error(field=None, error=e)
            return super().form_invalid(form)
        return res


class MovementListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = Movement
    table_class = MovementTable


class MovementCreateView(AuditFormMixin, CreateView):
    model = Movement
    form_class = MovementForm
    success_message = CREATE_SUCCESS_MESSAGE

    def form_valid(self, form):
        self.kwargs.update({'folder': form.instance.law_suit.folder_id})
        super(MovementCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse(
            'lawsuit_update',
            kwargs={
                'folder': self.kwargs['folder'],
                'pk': self.kwargs['lawsuit']
            })
        super(MovementCreateView, self).get_success_url()


class MovementUpdateView(AuditFormMixin, UpdateView):
    model = Movement
    form_class = MovementForm
    success_message = UPDATE_SUCCESS_MESSAGE

    def form_valid(self, form):
        self.kwargs.update({'folder': form.instance.law_suit.folder_id})
        super(MovementUpdateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse(
            'lawsuit_update',
            kwargs={
                'folder': self.kwargs['folder'],
                'pk': self.kwargs['lawsuit']
            })
        super(MovementUpdateView, self).get_success_url()

    def get_context_data(self, **kwargs):
        context = super(MovementUpdateView, self).get_context_data(**kwargs)
        cache.set('movement_page', self.request.META.get('HTTP_REFERER'))
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
        if cache.get('lawsuit_movement_page'):
            self.success_url = cache.get('lawsuit_movement_page')
        return super(MovementUpdateView, self).post(request, *args, **kwargs)


class MovementDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = Movement
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)

    def post(self, request, *args, **kwargs):
        self.success_url = urlparse(request.META.get('HTTP_REFERER')).path
        return super(MovementDeleteView, self).post(request, *args, **kwargs)


class MovementTaskCreateView(PopupMixin, SuccessMessageMixin,
                             CustomLoginRequiredView, GenericFormOneToMany,
                             CreateView):
    model = Movement
    related_model = Task
    form_class = MovementForm
    table_class = TaskTable
    template_name = 'lawsuit/movement_task_form.html'
    success_message = CREATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        context = super(MovementTaskCreateView,
                        self).get_context_data(**kwargs)
        if not self.is_popup:
            context['nav_' + self.related_model._meta.verbose_name] = True
            context['form_name'] = self.related_model._meta.verbose_name
            context[
                'form_name_plural'] = self.related_model._meta.verbose_name_plural
            table = self.table_class(self.related_model.objects.none())
            RequestConfig(
                self.request, paginate={
                    'per_page': 10
                }).configure(table)
            context['table'] = table
        return context

    def get_success_url(self):
        if self.is_popup:
            self.success_url = "{}?field=movement&value={}&label={}".format(
                reverse('popup_success'), self.object.id,
                self.object.type_movement.name)
        else:
            self.success_url = reverse(
                'lawsuit_update',
                kwargs={
                    'folder': self.kwargs['folder'],
                    'pk': self.kwargs['lawsuit']
                })

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class MovementTaskUpdateView(SuccessMessageMixin, CustomLoginRequiredView,
                             GenericFormOneToMany, UpdateView):
    model = Movement
    related_model = Task
    form_class = MovementForm
    table_class = TaskTable
    related_ordering = ('-final_deadline_date', )
    template_name = 'lawsuit/movement_task_form.html'
    success_message = CREATE_SUCCESS_MESSAGE

    def get_context_data(self, **kwargs):
        context = super(MovementTaskUpdateView,
                        self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        self.success_url = reverse(
            'lawsuit_update',
            kwargs={
                'folder': self.kwargs['folder'],
                'pk': self.kwargs['lawsuit']
            })

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class OrganCreateView(AuditFormMixin, CreateView):
    """
    Classe responsavel por fornecer a regra de criacao dos Orgaos
    """
    model = Organ
    form_class = OrganForm
    success_url = reverse_lazy('organ_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class OrganUpdateView(AuditFormMixin, UpdateView):
    """
    Classe responsavel por fornecer a regra de alteracao dos Orgaos
    """
    model = Organ
    form_class = OrganForm
    success_url = reverse_lazy('organ_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    object_list_url = 'organ_list'
    template_name_suffix = '_update_form'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'address_table':
            AddressOrganTable(self.object.address_set.all()),
        })
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class OrganDeleteView(CustomLoginRequiredView, MultiDeleteViewMixin):
    """
    Classe responsavel por forncer a regra de exclusao dos Orgaos
    """
    model = Organ
    success_url = reverse_lazy('organ_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class OrganListView(SuccessMessageMixin, SingleTableViewMixin):
    """
    Classe responsavel por fornecer a regra de listagem dos Orgaos
    """
    model = Organ
    table_class = OrganTable


class OrganAutocompleteView(TypeaHeadGenericSearch):
    @staticmethod
    def get_data(module, model, field, q, office, forward_params, extra_params,
                 *args, **kwargs):
        data = []
        court_district = extra_params.get('court_district')
        if court_district:
            for organ in Organ.objects.filter(
                    legal_name__unaccent__icontains=q,
                    court_district_id=court_district,
                    is_active=True,
                    office=office):
                data.append({
                    'id': organ.id,
                    'data-value-txt': organ.legal_name
                })
        return list(data)


class CourtDistrictAutocomplete(TypeaHeadGenericSearch):
    @staticmethod
    def get_data(module, model, field, q, office, forward_params, extra_params,
                 *args, **kwargs):
        data = []
        court_districts = CourtDistrict.objects.filter(
            **
            forward_params) if forward_params else CourtDistrict.objects.all()
        court_districts = court_districts.filter(
            Q(name__unaccent__icontains=q)
            | Q(state__initials__unaccent__icontains=q))
        for court_district in court_districts:
            data.append({
                'id': court_district.id,
                'data-value-txt': court_district.__str__()
            })
        return list(data)


class FolderAutocomplete(TypeaHeadGenericSearch):
    @staticmethod
    def get_data(module, model, field, q, office, forward_params, extra_params,
                 *args, **kwargs):
        data = []
        for folder in Folder.objects.filter(
                Q(office=office),
                Q(
                    Q(person_customer__legal_name__unaccent__istartswith=q)
                    | Q(folder_number__startswith=q))):
            data.append({'id': folder.id, 'data-value-txt': folder.__str__()})
        return list(data)


class LawsuitAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Folder.objects.none()

        if self.q:
            filters = Q(person_lawyer__name__unaccent__istartswith=self.q)
            filters |= Q(law_suit_number__startswith=self.q)
            qs = LawSuit.objects.filter(is_active=True).filter(filters)
        return qs

    def get_result_label(self, result):
        return "{} - {}".format(result.law_suit_number,
                                result.person_lawyer.name)


class MovementAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Movement.objects.none()

        if self.q:
            qs = Movement.objects.filter(
                is_active=True,
                type_movement__name__unaccent__icontains=self.q)
        return qs

    def get_result_label(self, result):
        return result.type_movement.name


class AddressOrganCreateView(AddressCreateView):
    def get_success_url(self):
        return reverse('organ_update', args=(self.object.person.pk, ))


class AddressOrganUpdateView(AddressUpdateView):
    def get_success_url(self):
        return reverse('organ_update', args=(self.object.person.pk, ))


class AddressOrganDeleteView(AddressDeleteView):
    def get_success_url(self):
        return reverse('organ_update', args=(self.object.person.pk, ))


class TypeaHeadCourtDistrictSearch(TypeaHeadGenericSearch):
    @staticmethod
    def get_data(module, model, field, q, office, forward_params, extra_params,
                 *args, **kwargs):
        data = []
        court_districts = CourtDistrict.objects.filter(
            **
            forward_params) if forward_params else CourtDistrict.objects.all()
        court_districts = court_districts.filter(Q(name__unaccent__icontains=q) |
                                                 Q(state__initials__unaccent__icontains=q))
        forward_field = extra_params.get('forward_field', None)
        if forward_field:
            forward_field = forward_field.replace('__', '.')
        for court_district in court_districts:
            data.append({
                'id': court_district.id,
                'data-value-txt': court_district.__str__(),
                'data-forward-id': eval('court_district.{}'.format(forward_field)) if forward_field else 0
            })
        return list(data)


class CourtDistrictComplementListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = CourtDistrictComplement
    table_class = CourtDistrictComplementTable


class CourtDistrictComplementCreateView(AuditFormMixin, CreateView):
    model = CourtDistrictComplement
    form_class = CourtDistrictComplementForm
    success_url = reverse_lazy('complement_list')
    success_message = CREATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CourtDistrictComplementUpdateView(AuditFormMixin, UpdateView):
    model = CourtDistrictComplement
    form_class = CourtDistrictComplementForm
    success_url = reverse_lazy('complement_list')
    success_message = UPDATE_SUCCESS_MESSAGE

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CourtDistrictComplementDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = CourtDistrictComplement
    success_url = reverse_lazy('complement_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)


class TypeaHeadCourtDistrictComplementSearch(TypeaHeadGenericSearch):
    @staticmethod
    def get_data(module, model, field, q, office, forward_params, extra_params,
                 *args, **kwargs):
        data = []
        complements = CourtDistrictComplement.objects.get_queryset(office=[office.id]).filter(
            **forward_params) if forward_params else CourtDistrictComplement.objects.get_queryset(office=[office.id])
        complement_name = court_district = q
        if len(q.split(' - ')) == 2:
            complement_name, court_district = q.split(' - ')
            court_district = court_district.split(' (')[0]
        complements = complements.filter(Q(name__unaccent__icontains=complement_name)|
                                         Q(court_district__name__unaccent__icontains=court_district))
        state = extra_params.get('state', None)
        if state:
            complements = complements.filter(Q(court_district__state__id=state))
        forward_field = extra_params.get('forward_field', None)
        if forward_field:
            forward_field = forward_field.replace('__', '.')
        for complement in complements:
            data.append({
                'id': complement.id,
                'data-value-txt': '{} - {}'.format(complement.name, complement.court_district.__str__()),
                'data-forward-id': eval('complement.{}'.format(forward_field)) if forward_field else 0,
                'data-extra-params': complement.court_district.state.id
            })
        return list(data)
