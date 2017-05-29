from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
# project imports
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django_tables2 import RequestConfig, SingleTableView

from core.messages import new_success, update_success
from core.views import BaseCustomView
from .forms import TypeMovementForm, InstanceForm, MovementForm, FolderForm, LawSuitForm, CourtDistrictForm
from .models import TypeMovement, Instance, Movement, LawSuit, Folder, CourtDistrict
from .tables import TypeMovementTable, MovementTable, FolderTable, LawSuitTable, CourtDistrictTable


class InstanceUpdateView(BaseCustomView, UpdateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceDeleteView(BaseCustomView, DeleteView):
    model = Instance
    success_url = reverse_lazy('instance_list')

    # Sobrescreve a função Delete da classe DeleteView. Pois a exclusão de um elemento é
    # Tornar o flag Active = False e não remover a linha
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        success_url = self.success_url
        instance_id = int(instance.id)
        Instance.objects.filter(id=instance_id).update(active=False)
        return HttpResponseRedirect(success_url)


class InstanceCreateView(BaseCustomView, CreateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceListView(ListView):
    model = Instance
    queryset = Instance.objects.filter(active=True)


class TypeMovementListView(LoginRequiredMixin, SingleTableView):
    model = TypeMovement
    table_class = TypeMovementTable
    queryset = TypeMovement.objects.all()
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super(TypeMovementListView, self).get_context_data(**kwargs)
        context['nav_type_movement'] = True
        context['form_name'] = TypeMovement._meta.verbose_name
        context['form_name_plural'] = TypeMovement._meta.verbose_name_plural
        table = TypeMovementTable(TypeMovement.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class TypeMovementDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = TypeMovement
    success_url = reverse_lazy('type_movement_list')

    def delete(self, request, *args, **kwargs):
        typemovement = self.get_object()
        typemovement_id = int(typemovement.id)
        TypeMovement.objects.filter(id=typemovement_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class MovementListView(LoginRequiredMixin, SingleTableView):
    model = Movement
    table_class = MovementTable
    queryset = Movement.objects.all()
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super(MovementListView, self).get_context_data(**kwargs)
        context['nav_movement'] = True
        table = MovementTable(Movement.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class MovementDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = Movement
    success_url = reverse_lazy('movement_list')

    def delete(self, request, *args, **kwargs):
        movement = self.get_object()
        movement_id = int(movement.id)
        Movement.objects.filter(id=movement_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class FolderListView(LoginRequiredMixin, SingleTableView):
    model = Folder
    queryset = Folder.objects.all()  # filter(active=True)
    ordering = ['id']
    table_class = FolderTable

    def get_context_data(self, **kwargs):
        context = super(FolderListView, self).get_context_data(**kwargs)
        context['nav_folder'] = True
        table = FolderTable(Folder.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class FolderDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = Folder
    success_url = reverse_lazy('folder-list')

    def delete(self, request, *args, **kwargs):
        folder = self.get_object()
        folder_id = int(folder.id)
        Movement.objects.filter(id=folder_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class LawSuitListView(LoginRequiredMixin, SingleTableView):
    model = LawSuit
    queryset = LawSuit.objects.all()
    ordering = ['-id']
    table_class = LawSuitTable

    def get_context_data(self, **kwargs):
        context = super(LawSuitListView, self).get_context_data(**kwargs)
        context['nav_lawsuit'] = True
        table = LawSuitTable(LawSuit.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class LawSuitDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = LawSuit
    success_url = reverse_lazy('lawsuit_list')

    def delete(self, request, *args, **kwargs):
        lawsuit = self.get_object()
        lawsuit_id = int(lawsuit.id)
        LawSuit.objects.filter(id=lawsuit_id).update(active=False)
        return HttpResponseRedirect(self.success_url)


class CourtDistrictListView(LoginRequiredMixin, SingleTableView):
    model = CourtDistrict
    table_class = CourtDistrictTable
    queryset = CourtDistrict.objects.all()
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(CourtDistrictListView, self).get_context_data(**kwargs)
        context['nav_courtdistrict'] = True
        table = CourtDistrictTable(CourtDistrict.objects.all().order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 10}).configure(table)
        context['table'] = table
        return context


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


class CourtDistrictDeleteView(LoginRequiredMixin, BaseCustomView, DeleteView):
    model = CourtDistrict
    success_url = reverse_lazy('courtdistrict_list')

    def delete(self, request, *args, **kwargs):
        courtdistrict = self.get_object()
        courtdistrict_id = int(courtdistrict.id)
        CourtDistrict.objects.filter(id=courtdistrict_id).update(active=False)
        return HttpResponseRedirect(self.success_url)
