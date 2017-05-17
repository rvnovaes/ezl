from django.http import HttpResponseRedirect

# python imports
from datetime import datetime

# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy

# project imports
from django.template.response import TemplateResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_tables2 import RequestConfig

from .forms import TypeMovementForm, InstanceForm
from .models import TypeMovement, Instance
from .tables import TypeMovementTable
from core.views import BaseCustomView



class InstanceUpdateView(BaseCustomView, UpdateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceCreateView(BaseCustomView, CreateView):
    model = Instance
    form_class = InstanceForm
    success_url = reverse_lazy('instance_list')


class InstanceListView(ListView):
    model = Instance
    queryset = Instance.objects.filter(active=True)


class TypeMovementListView(ListView):
    model = TypeMovement
    queryset = TypeMovement.objects.filter(active=True)
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super(TypeMovementListView, self).get_context_data(**kwargs)
        context['nav_type_movement'] = True
        table = TypeMovementTable(TypeMovement.objects.filter(active=True).order_by('-pk'))
        RequestConfig(self.request, paginate={'per_page': 30}).configure(table)
        context['table'] = table
        return context

    
class TypeMovementCreateView(BaseCustomView,CreateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')


class TypeMovementUpdateView(BaseCustomView,UpdateView):
    model = TypeMovement
    form_class = TypeMovementForm
    success_url = reverse_lazy('type_movement_list')

      
class TypeMovementDeleteView(BaseCustomView,DeleteView):
    model = TypeMovement
    success_url = reverse_lazy('type_movement_list')

    def delete(self, request, *args, **kwargs):
        typemovement = self.get_object()
        typemovement_id = int(typemovement.id)
        TypeMovement.objects.filter(id=typemovement_id).update(active=False)
        return HttpResponseRedirect(self.success_url)

   

