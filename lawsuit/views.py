from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
# python imports
from datetime import datetime

# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.views import View
from django.views.generic.list import ListView

# project imports
from django.template.response import TemplateResponse

from .forms import TypeMovementForm, InstanceForm
from .models import TypeMovement, Instance
from core.views import BaseCustomView
from django.views.generic import CreateView, UpdateView


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


class TypeMovementList(ListView):
    model = TypeMovement
    queryset = TypeMovement.objects.filter(active=True)


def type_movement(request, type_movement_id):
    type_movement_id = int(type_movement_id)
    post = request.POST.copy()
    post['uses_wo'] = 'off' if 'uses_wo' not in post and type_movement_id else 'on'

    if request.method == 'GET':
        type_movement_form = TypeMovementForm(request.GET)
    else:
        type_movement_form = TypeMovementForm(post)

    # TODO implementação a lógica para verficiar se o usuário está atuenticado

    if type_movement_id > 0:
        try:
            type_movement = TypeMovement.objects.get(id=type_movement_id)
        except ObjectDoesNotExist:
            type_movement = TypeMovement()
            type_movement.name = type_movement_form.cleaned_data['name']
            type_movement.legacy_code = type_movement_form.cleaned_data['legacy_code']
            type_movement.uses_wo = type_movement_form.cleaned_data['uses_wo']#True if 'uses_wo' in type_movement_form.cleaned_data else False

        if type_movement_id > 0:
            # carrega o tipo de movimento no form
            if request.method == 'GET':
                type_movement_dict = dict()
                # transforma o modelo em dicionario para carregar na tela direto do modelo
                type_movement_dict.update(model_to_dict(type_movement))

                type_movement_form = TypeMovementForm(initial=type_movement_dict)
            else:
                type_movement.alter_user_id = request.user.id
                type_movement.alter_date = datetime.now()
                # altera o Tipo de Movimento
                type_movement.save()

                messages.add_message(request, messages.SUCCESS, u'Tipo de Movimento atualizado com sucesso.')
                return HttpResponseRedirect('/processos/cadastro-tipo-movimentacao/')
        else:
            if request.method == 'POST':
                # cria novo Tipo de Movimento
                TypeMovement.objects.create(
                    name=type_movement.name,
                    legacy_code=type_movement.legacy_code,
                    uses_wo=type_movement.uses_wo,
                    create_user_id=request.user.id,
                    create_date=datetime.now(),
                ).save()

                messages.add_message(request, messages.SUCCESS, u'Tipo de Movimento salvo com sucesso.')
    else:
        type_movement_form = TypeMovementForm()

    return render(request, 'lawsuit/type_movement.html', {'form': type_movement_form,
                                                          'type_movement_id': type_movement_id,
                                                          'title_page': 'Cadastro de Tipos de Movimentação'})


