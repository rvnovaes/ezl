from django.http import HttpResponseRedirect

# python imports
from datetime import datetime

# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.views.generic.list import ListView

# project imports
from .forms import TypeMovementForm
from .models import TypeMovement


class TypeMovementList(ListView):
    model = TypeMovement
    queryset = TypeMovement.objects.filter(active=True)


def type_movement_list(request):
    try:
        type_movements = TypeMovement.objects.filter(active=True)
    except ObjectDoesNotExist:
        type_movements = None
    return render(request, 'lawsuit/typemovement_list.html', {'typemovement_list': type_movements})

def type_movement(request):
    if request.method == 'POST':
        form = TypeMovementForm(request.POST)

        if form.is_valid():
            type_movement = TypeMovement()
            type_movement.name = form.cleaned_data['name']
            type_movement.legacy_code = form.cleaned_data['legacy_code']
            type_movement.uses_wo = form.cleaned_data['uses_wo']#True if 'uses_wo' in type_movement_form.cleaned_data else False

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
        form = TypeMovementForm()



    return render(request, 'lawsuit/type_movement.html', {'form': type_movement_form,
                                                          'type_movement_id': type_movement_id,
                                                          'title_page': 'Cadastro de Tipos de Movimentação'})
