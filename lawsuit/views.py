from django.http import HttpResponseRedirect

# python imports
from datetime import datetime

# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse, reverse_lazy, resolve

# project imports
from django.template.response import TemplateResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View
from django_tables2 import RequestConfig

from .forms import TypeMovementForm, InstanceForm
from .models import TypeMovement, Instance
from .tables import TypeMovementTable
from core.views import BaseCustomView


class TypeMovementListView(BaseCustomView, ListView):
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


# Lista intancias cadastradas no sistema
def instances(request):

    try:
        instances_list = Instance.objects.filter(active=True)

        instances_list_number = len(instances_list)

        if instances_list_number > 0:
            context = {'instances': instances_list}
        else:
            instances_list = None
            context = {'instances': instances_list}

        return render(request, 'lawsuit/instances.html', context)

    except:
        instances_list = None
        return render(request, 'lawsuit/instances.html', {'instances': instances_list})


def delete_instance(request, id_instance):

    try:
        Instance.objects.filter(id=id_instance).update(active=False)
        messages.add_message(request,messages.INFO,"Instância apagada com sucesso.")
        return HttpResponseRedirect('/processos/instancias/')

    except:
        messages.add_message("Erro ao apagar instância.")
        TemplateResponse('lawsuit/instances.html', {'message': 'Erro ao apagar instância.', })
        return HttpResponseRedirect('/processos/instancias/')


def instance(request):

    if request.method == 'POST':
        form = InstanceForm(request.POST)

        # Verifica se o usuário submeteu dados válidos ao formulário
        if form.is_valid():

            try:
                # Instancia o objeto "Instancia" de acordo com seu modelo
                instance = Instance.objects.create(
                    name=form.cleaned_data['name'],
                    create_user_id=request.user.id,
                    create_date=datetime.now(),
                )
                # Salva o objeto no banco de dados
                instance.save()
                messages.add_message(request, messages.SUCCESS, "Dados salvos com sucesso.")

            except:
                messages.add_message(request,messages.ERROR,"Ocorreram erros de validação no formulário.")
        else:
            messages.add_message(request, messages.ERROR, "Ocorreram erros de validação no formulário.")

        return HttpResponseRedirect('/processos/instancias/')

    else:
        form = InstanceForm()
        return render(request,'lawsuit/instance.html',{'form':form,
                                                      'title_page': 'Instâncias - Easy Lawyer'})