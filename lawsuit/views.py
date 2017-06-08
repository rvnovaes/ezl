from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
# project imports
from django.views.generic.edit import CreateView, UpdateView
from django_tables2 import RequestConfig, SingleTableView

from core.messages import new_success, update_success, delete_success
from core.views import BaseCustomView, MultiDeleteViewMixin, SingleTableViewMixin, CreateViewMixin
from .forms import LawSuitInstanceForm
from .forms import TypeMovementForm, InstanceForm, MovementForm, FolderForm, LawSuitForm, CourtDistrictForm
from .models import LawSuitInstance
from .models import TypeMovement, Instance, Movement, LawSuit, Folder, CourtDistrict
from .tables import LawSuitInstanceTable
from .tables import TypeMovementTable, MovementTable, FolderTable, LawSuitTable, CourtDistrictTable, InstanceTable


class InstanceListView(LoginRequiredMixin, SingleTableView):
    model = Instance
    table_class = InstanceTable
    queryset = Instance.objects.all()
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super(InstanceListView, self).get_context_data(**kwargs)
        context['nav_instance'] = True
        context['form_name_plural'] = Instance._meta.verbose_name_plural
        table = InstanceTable(Instance.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class MovementListView(LoginRequiredMixin, SingleTableViewMixin):
    model = Movement
    table_class = MovementTable

    # def get_context_data(self, **kwargs):
    #     context = super(MovementListView, self).get_context_data(**kwargs)
    #     context['nav_movement'] = True
    #     table = MovementTable(Movement.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class MovementCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = Movement
    form_class = MovementForm
    success_url = reverse_lazy('movement_list')
    success_message = new_success


class MovementUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = Movement
    form_class = MovementForm
    success_url = reverse_lazy('movement_list')
    success_message = update_success


class MovementDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = Movement
    success_url = reverse_lazy('movement_list')
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


class LawSuitListView(LoginRequiredMixin, SingleTableViewMixin):
    model = LawSuit
    table_class = LawSuitTable

    # def get_context_data(self, **kwargs):
    #     context = super(LawSuitListView, self).get_context_data(**kwargs)
    #     context['nav_lawsuit'] = True
    #     table = LawSuitTable(LawSuit.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class LawSuitCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = LawSuit
    form_class = LawSuitForm
    success_url = reverse_lazy('lawsuit_list')
    success_message = new_success


class LawSuitUpdateView(LoginRequiredMixin, BaseCustomView, UpdateView):
    model = LawSuit
    form_class = LawSuitForm
    success_url = reverse_lazy('lawsuit_list')
    success_message = update_success


class LawSuitDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = LawSuit
    success_url = reverse_lazy('lawsuit_list')
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


class LawSuitInstanceListView(LoginRequiredMixin, SingleTableViewMixin):
    model = LawSuitInstance
    table_class = LawSuitInstanceTable

    # def get_context_data(self, **kwargs):
    #     context = super(LawSuitInstanceListView, self).get_context_data(**kwargs)
    #     context['nav_lawsuitinstance'] = True
    #     table = LawSuitInstanceTable(LawSuitInstance.objects.all().order_by('-pk'))
    #     RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
    #     context['table'] = table
    #     return context


class LawSuitInstanceCreateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, CreateView):
    model = LawSuitInstance
    form_class = LawSuitInstanceForm
    success_url = reverse_lazy('lawsuitinstance_list')
    success_message = new_success


class LawSuitInstanceUpdateView(SuccessMessageMixin, LoginRequiredMixin, BaseCustomView, UpdateView):
    model = LawSuitInstance
    form_class = LawSuitInstanceForm
    success_url = reverse_lazy('lawsuitinstance_list')
    success_message = update_success


class LawSuitInstanceDeleteView(LoginRequiredMixin, BaseCustomView, MultiDeleteViewMixin):
    model = LawSuitInstance
    success_url = reverse_lazy('lawsuitinstance_list')
    success_message = delete_success(model._meta.verbose_name_plural)
    # def delete(self, request, *args, **kwargs):
    #     law_suit_instance = self.get_object()
    #     law_suit_instance_id = int(law_suit_instance.id)
    #     LawSuitInstance.objects.filter(id=law_suit_instance_id).update(active=False)
    #     return HttpResponseRedirect(self.success_url)
