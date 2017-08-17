from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy, reverse
# project imports
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_tables2 import RequestConfig

from core.messages import new_success, update_success, delete_success, delete_error_protected
from core.views import BaseCustomView, MultiDeleteViewMixin, SingleTableViewMixin, GenericFormOneToMany
from task.models import Task
from task.tables import TaskTable
from .forms import TypeMovementForm, InstanceForm, MovementForm, FolderForm, LawSuitForm, CourtDistrictForm, \
    CourtDivisionForm
from .models import Instance, Movement, LawSuit, Folder, CourtDistrict, CourtDivision, TypeMovement
from .tables import MovementTable, FolderTable, LawSuitTable, CourtDistrictTable, InstanceTable, \
    CourtDivisionTable, TypeMovementTable


class InstanceListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Instance
    table_class = InstanceTable
    # queryset = Instance.objects.all()
    # ordering = ['-id']

    # def get_context_data(self, **kwargs):
    #     context = super(InstanceListView, self).get_context_data(**kwargs)
    #     context['nav_instance'] = True
    #     context['form_name_plural'] = Instance._meta.verbose_name_plural
    #     table = InstanceTable(Instance.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class InstanceCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceDeleteView(SuccessMessageMixin, LoginRequiredMixin, MultiDeleteViewMixin):
    model = Instance
    success_url = reverse_lazy('instance_list')
    success_message = delete_success('instâncias')


class TypeMovementListView(LoginRequiredMixin, SingleTableViewMixin):
    model = TypeMovement
    table_class = TypeMovementTable

    # def get_context_data(self, **kwargs):
    #     context = super(TypeMovementListView, self).get_context_data(**kwargs)
    #     context['nav_type_movement'] = True
    #     context['form_name'] = TypeMovement._meta.verbose_name
    #     context['form_name_plural'] = TypeMovement._meta.verbose_name_plural
    #     table = TypeMovementTable(TypeMovement.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class TypeMovementCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')
    success_message = new_success


class TypeMovementUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')
    success_message = update_success


class TypeMovementDeleteView(LoginRequiredMixin, MultiDeleteViewMixin):
    model = TypeMovement
    success_url = reverse_lazy('type_movement_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class FolderListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Folder
    table_class = FolderTable


class FolderCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folder_list')
    success_message = new_success


class FolderUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folder_list')
    success_message = update_success


class FolderDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = Folder
    success_url = reverse_lazy('folder_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class CourtDistrictListView(LoginRequiredMixin, SingleTableViewMixin):
    model = CourtDistrict
    table_class = CourtDistrictTable

    # def get_context_data(self, **kwargs):
    #     context = super(CourtDistrictListView, self).get_context_data(**kwargs)
    #     context['nav_courtdistrict'] = True
    #     table = CourtDistrictTable(CourtDistrict.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class CourtDistrictCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = CourtDistrict
    form_class = CourtDistrictForm
    success_url = reverse_lazy('courtdistrict_list')
    success_message = new_success


class CourtDistrictUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = CourtDistrict
    form_class = CourtDistrictForm
    success_url = reverse_lazy('courtdistrict_list')
    success_message = update_success


class CourtDistrictDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = CourtDistrict
    success_url = reverse_lazy('courtdistrict_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class CourtDivisionListView(LoginRequiredMixin, SingleTableViewMixin):
    model = CourtDivision
    table_class = CourtDivisionTable

    # def get_context_data(self, **kwargs):
    #     context = super(CourtDistrictListView, self).get_context_data(**kwargs)
    #     context['nav_courtdistrict'] = True
    #     table = CourtDistrictTable(CourtDistrict.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class CourtDivisionCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = CourtDivision
    form_class = CourtDivisionForm
    success_url = reverse_lazy('courtdivision_list')
    success_message = new_success


class CourtDivisionUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = CourtDivision
    form_class = CourtDivisionForm
    success_url = reverse_lazy('courtdivision_list')
    success_message = update_success


class CourtDivisionDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = CourtDivision
    success_url = reverse_lazy('courtdivision_list')
    success_message = delete_success(model._meta.verbose_name_plural)


class FolderLawsuitCreateView(SuccessMessageMixin, GenericFormOneToMany, CreateView):
    model = Folder
    related_model = LawSuit
    form_class = FolderForm
    table_class = LawSuitTable
    template_name = 'lawsuit/folder_lawsuit_form.html'
    success_url = reverse_lazy('folder_list')
    success_message = new_success

    def get_context_data(self, **kwargs):
        context = super(FolderLawsuitCreateView, self).get_context_data(**kwargs)
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.none())
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


class FolderLawsuitUpdateView(SuccessMessageMixin, GenericFormOneToMany, UpdateView):
    model = Folder
    related_model = LawSuit
    form_class = FolderForm
    table_class = LawSuitTable
    template_name = 'lawsuit/folder_lawsuit_form.html'
    success_url = reverse_lazy('folder_list')
    success_message = update_success
    delete_message = delete_success(related_model._meta.verbose_name_plural)

    def get_context_data(self, **kwargs):
        context = super(FolderLawsuitUpdateView, self).get_context_data(**kwargs)
        related_model_id = self.kwargs['pk']
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.filter(folder__id=related_model_id).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


class LawSuitListView(LoginRequiredMixin, SingleTableViewMixin):
    model = LawSuit
    table_class = LawSuitTable


class LawSuitCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = LawSuit
    form_class = LawSuitForm
    success_message = new_success

    def get_success_url(self):
        self.success_url = reverse('folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawSuitCreateView, self).get_success_url()


class LawSuitUpdateView(LoginRequiredMixin, BaseCustomView, UpdateView):
    model = LawSuit
    form_class = LawSuitForm
    success_message = update_success

    def get_success_url(self):
        self.success_url = reverse('folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawSuitUpdateView, self).get_success_url()


class LawSuitDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = LawSuit
    success_message = delete_success(model._meta.verbose_name_plural)

    def delete(self, request, *args, **kwargs):
        pks = self.request.POST.getlist("selection")
        parent_class = self.request.POST['parent_class']
        try:
            self.model.objects.filter(pk__in=pks).delete()
            messages.success(self.request, delete_success(self.model._meta.verbose_name_plural))
        except ProtectedError as e:
            qs = e.protected_objects.first()
            messages.error(self.request,
                           delete_error_protected(self.model._meta.verbose_name
                                                  , qs.__str__()))
        return HttpResponseRedirect(
            reverse('folder_update',
                    kwargs={'pk': parent_class}))


class LawsuitMovementCreateView(SuccessMessageMixin, LoginRequiredMixin, GenericFormOneToMany, CreateView):
    model = LawSuit
    related_model = Movement
    form_class = LawSuitForm
    table_class = MovementTable
    template_name = 'lawsuit/lawsuit_movement_form.html'
    # success_url = reverse_lazy('lawsuit_list')
    success_message = new_success

    def get_context_data(self, **kwargs):
        context = super(LawsuitMovementCreateView, self).get_context_data(**kwargs)
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.none())
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get_success_url(self):
        self.success_url = reverse('folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawsuitMovementCreateView, self).get_success_url()


class LawsuitMovementUpdateView(SuccessMessageMixin, LoginRequiredMixin, GenericFormOneToMany, UpdateView):
    model = LawSuit
    related_model = Movement
    form_class = LawSuitForm
    table_class = MovementTable
    template_name = 'lawsuit/lawsuit_movement_form.html'
    success_message = update_success
    delete_message = delete_success(related_model._meta.verbose_name_plural)

    def get_context_data(self, **kwargs):
        context = super(LawsuitMovementUpdateView, self).get_context_data(**kwargs)
        related_model_id = self.kwargs['pk']
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.filter(law_suit__id=related_model_id).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get_success_url(self):
        self.success_url = reverse('folder_update', kwargs={'pk': self.kwargs['folder']})
        super(LawsuitMovementUpdateView, self).get_success_url()


class MovementListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Movement
    table_class = MovementTable


class MovementCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Movement
    form_class = MovementForm
    success_message = new_success

    def form_valid(self, form):
        self.kwargs.update({'folder': form.instance.law_suit.folder_id})
        super(MovementCreateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse('lawsuit_update',
                                   kwargs={'folder': self.kwargs['folder'], 'pk': self.kwargs['lawsuit']})
        super(MovementCreateView, self).get_success_url()


class MovementUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Movement
    form_class = MovementForm
    success_message = update_success

    def form_valid(self, form):
        self.kwargs.update({'folder': form.instance.law_suit.folder_id})
        super(MovementUpdateView, self).form_valid(form)
        return HttpResponseRedirect(self.success_url)

    def get_success_url(self):
        self.success_url = reverse('lawsuit_update',
                                   kwargs={'folder': self.kwargs['folder'], 'pk': self.kwargs['lawsuit']})
        super(MovementUpdateView, self).get_success_url()


class MovementDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = Movement
    success_message = delete_success(model._meta.verbose_name_plural)

    def delete(self, request, *args, **kwargs):
        pks = self.request.POST.getlist("selection")
        parent_class = self.request.POST['parent_class']
        try:
            self.model.objects.filter(pk__in=pks).delete()
            messages.success(self.request, delete_success(self.model._meta.verbose_name_plural))
        except ProtectedError as e:
            qs = e.protected_objects.first()
            messages.error(self.request,
                           delete_error_protected(self.model._meta.verbose_name
                                                  , qs.__str__()))
        return HttpResponseRedirect(
            reverse('lawsuit_update',
                    kwargs={'pk': parent_class}))


class MovementTaskCreateView(SuccessMessageMixin, LoginRequiredMixin, GenericFormOneToMany, CreateView):
    model = Movement
    related_model = Task
    form_class = MovementForm
    table_class = TaskTable
    template_name = 'lawsuit/movement_task_form.html'
    success_message = new_success

    def get_context_data(self, **kwargs):
        context = super(MovementTaskCreateView, self).get_context_data(**kwargs)
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.none())
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get_success_url(self):
        self.success_url = reverse('lawsuit_update', kwargs={'pk': self.kwargs['lawsuit']})
        super(MovementTaskCreateView, self).get_success_url()


class MovementTaskUpdateView(SuccessMessageMixin, LoginRequiredMixin, GenericFormOneToMany, UpdateView):
    model = Movement
    related_model = Task
    form_class = MovementForm
    table_class = TaskTable
    template_name = 'lawsuit/movement_task_form.html'
    success_message = new_success

    def get_context_data(self, **kwargs):
        context = super(MovementTaskUpdateView, self).get_context_data(**kwargs)
        related_model_id = self.kwargs['pk']
        context['nav_' + self.related_model._meta.verbose_name] = True
        context['form_name'] = self.related_model._meta.verbose_name
        context['form_name_plural'] = self.related_model._meta.verbose_name_plural
        table = self.table_class(self.related_model.objects.filter(movement_id=related_model_id).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context

    def get_success_url(self):
        self.success_url = reverse('lawsuit_update', kwargs={'pk': self.kwargs['lawsuit']})
        super(MovementTaskUpdateView, self).get_success_url()
