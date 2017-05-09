import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

# python imports
from datetime import datetime


# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.forms.models import model_to_dict

# project imports
from .forms import TypeMovementForm
from .models import TypeMovement


def type_movement(request,type_movement_id):
    type_movement_form = TypeMovementForm(request.POST)

    # TODO implementação a lógica para verficiar se o usuário está atuenticado
    type_movement_id = int(type_movement_id)

    if type_movement_id>0:
        try:
            type_movement = TypeMovement.objects.get(id_type_movement=type_movement_id)
        except ObjectDoesNotExist:
            type_movement = TypeMovement()
    else:
        type_movement = TypeMovement()

    if type_movement_form.is_valid():
        type_movement.name = type_movement_form.cleaned_data['name']
        type_movement.legacy_code = type_movement_form.cleaned_data['legacy_code']
        type_movement.uses_wo = type_movement_form.cleaned_data['uses_wo']

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

            messages.add_message(request, messages.SUCCESS, u'Tipo de Movimento salvo com sucesso.')
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

    return render(request, 'lawsuit/type_movement.html', {'form': type_movement_form, 'type_movement_id': type_movement_id, 'title_page': 'Cadastro de Tipos de Movimentação'})
