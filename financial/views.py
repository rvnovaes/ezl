from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from django.views.generic.edit import CreateView, UpdateView
from core.messages import (CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE,
                           DELETE_SUCCESS_MESSAGE)
from core.views import (AuditFormMixin, MultiDeleteViewMixin,
                        SingleTableViewMixin)
from .forms import CostCenterForm, ServicePriceTableForm
from .models import CostCenter, ServicePriceTable
from .tables import CostCenterTable, ServicePriceTableTable
from core.views import remove_invalid_registry
from dal import autocomplete


class CostCenterListView(LoginRequiredMixin, SingleTableViewMixin):
    model = CostCenter
    table_class = CostCenterTable
    ordering = ('name', )

    @remove_invalid_registry
    def get_context_data(self, **kwargs):
        """
        Sobrescreve o metodo get_context_data utilizando o decorator
        remove_invalid_registry para remover o registro invalido da listagem
        :param kwargs:
        :return: Retorna o contexto contendo a listagem
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        return context


class CostCenterCreateView(AuditFormMixin, CreateView):
    model = CostCenter
    form_class = CostCenterForm
    success_url = reverse_lazy('costcenter_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'costcenter_list'


class CostCenterUpdateView(AuditFormMixin, UpdateView):
    model = CostCenter
    form_class = CostCenterForm
    success_url = reverse_lazy('costcenter_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'costcenter_list'


class CostCenterDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = CostCenter
    success_url = reverse_lazy('costcenter_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'costcenter_list'


class CostCenterAutocomplete(LoginRequiredMixin,
                             autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = CostCenter.objects.none()

        if self.q:
            qs = CostCenter.objects.filter(name__unaccent__istartswith=self.q,
                                           is_active=True)
        return qs


class ServicePriceTableListView(LoginRequiredMixin, SingleTableViewMixin):
    model = ServicePriceTable
    table_class = ServicePriceTableTable
    ordering = ('correspondent', )
    paginate_by = 30


class ServicePriceTableCreateView(AuditFormMixin, CreateView):
    model = ServicePriceTable
    form_class = ServicePriceTableForm
    success_url = reverse_lazy('servicepricetable_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'servicepricetable_list'


class ServicePriceTableUpdateView(AuditFormMixin, UpdateView):
    model = ServicePriceTable
    form_class = ServicePriceTableForm
    success_url = reverse_lazy('servicepricetable_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'servicepricetable_list'


class ServicePriceTableDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = ServicePriceTable
    success_url = reverse_lazy('servicepricetable_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'servicepricetable_list'
