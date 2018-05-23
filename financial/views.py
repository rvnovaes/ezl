from core.views import CustomLoginRequiredView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q

from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from core.messages import (CREATE_SUCCESS_MESSAGE, UPDATE_SUCCESS_MESSAGE,
                           DELETE_SUCCESS_MESSAGE)
from core.models import Office
from core.views import (AuditFormMixin, MultiDeleteViewMixin,
                        SingleTableViewMixin)
from .forms import CostCenterForm, ServicePriceTableForm, ImportServicePriceTableForm
from .models import CostCenter, ServicePriceTable
from .tables import CostCenterTable, ServicePriceTableTable
from .tasks import import_xls_service_price_table
from core.views import remove_invalid_registry, TypeaHeadGenericSearch
from core.utils import get_office_session


class CostCenterListView(CustomLoginRequiredView, SingleTableViewMixin):
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

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CostCenterUpdateView(AuditFormMixin, UpdateView):
    model = CostCenter
    form_class = CostCenterForm
    success_url = reverse_lazy('costcenter_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'costcenter_list'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class CostCenterDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = CostCenter
    success_url = reverse_lazy('costcenter_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'costcenter_list'

    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        return ret


class CostCenterAutocomplete(TypeaHeadGenericSearch):

    @staticmethod
    def get_data(module, model, field, q, office, forward_params):
        data = []
        for cost_center in CostCenter.objects.filter(Q(name__unaccent__icontains=q),
                                                     Q(is_active=True),
                                                     Q(office=office)):
            data.append({'id': cost_center.id, 'data-value-txt': cost_center.__str__()})
        return list(data)


class ServicePriceTableListView(CustomLoginRequiredView, SingleTableViewMixin):
    model = ServicePriceTable
    table_class = ServicePriceTableTable
    ordering = ('office', )
    paginate_by = 30


class ServicePriceTableCreateView(AuditFormMixin, CreateView):
    model = ServicePriceTable
    form_class = ServicePriceTableForm
    success_url = reverse_lazy('servicepricetable_list')
    success_message = CREATE_SUCCESS_MESSAGE
    object_list_url = 'servicepricetable_list'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class ServicePriceTableUpdateView(AuditFormMixin, UpdateView):
    model = ServicePriceTable
    form_class = ServicePriceTableForm
    success_url = reverse_lazy('servicepricetable_list')
    success_message = UPDATE_SUCCESS_MESSAGE
    template_name_suffix = '_update_form'
    object_list_url = 'servicepricetable_list'

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw


class ServicePriceTableDeleteView(AuditFormMixin, MultiDeleteViewMixin):
    model = ServicePriceTable
    success_url = reverse_lazy('servicepricetable_list')
    success_message = DELETE_SUCCESS_MESSAGE.format(
        model._meta.verbose_name_plural)
    object_list_url = 'servicepricetable_list'


@login_required
def import_service_price_table(request):   
    context = { }    
    if request.method == 'POST':                     
        form = ImportServicePriceTableForm(request.POST, request.FILES)        
        if form.is_valid():
            if not request.FILES['file_xls'].name.endswith('.xlsx'):
                # pensar melhor forma de exibir mensagem
                pass
                
            file_xls = form.save(commit=False)
            file_xls.office = get_office_session(request)
            file_xls.create_user = request.user
            file_xls.save()
            
            import_xls_service_price_table.delay(file_xls.pk)
                        
            # if errors:
                # context['errors'] = errors            
    else:
        form = ImportServicePriceTableForm()
    context['form'] = form
    return render(request, 'core/import_service_price_table.html', context)
