import json
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core import serializers
from django.contrib import messages

# python imports
from datetime import datetime


# django imports
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, render_to_response
from django.forms.models import model_to_dict

# project imports
from django.template.response import TemplateResponse

from .forms import TypeMovementForm, InstanceForm
from .models import TypeMovement, Instance


def type_movement_list(request):
    try:
        type_movements_list = TypeMovement.objects.all()
    except ObjectDoesNotExist:
        type_movements_list = None

    form = TypeMovementForm(request.GET)

    if type_movements_list:
        return render(request, 'lawsuit/type_movements.html', {'form': form, 'type_movements_list': type_movements_list})
    else:
        return render(request, 'lawsuit/type_movements.html', {'form': form})


def type_movement_crud(request, type_movement_id):
    type_movement_form = TypeMovementForm(request.POST)

    # TODO implementação a lógica para verficiar se o usuário está atuenticado
    type_movement_id = int(type_movement_id)

    if type_movement_id>0:
        try:
            type_movement = TypeMovement.objects.get(id=type_movement_id)
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

            messages.add_message(request, messages.SUCCESS, u'Tipo de Movimento atualizado com sucesso.')
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

    return render(request, 'lawsuit/type_movement.html', {'form': type_movement_form,
                                                          'type_movement_id': type_movement_id,
                                                          'title_page': 'Cadastro de Tipos de Movimentação'})


def instance(request):

    try:
        instances_list = Instance.objects.all()
        instances_list_number = Instance.objects.all().count()

        if instances_list_number > 0:
            context = {'instances': instances_list}

        else:
            instances_list = None
            context = {'instances': instances_list}

        return render(request, 'lawsuit/instancias.html', context)

    except:
        instances_list = None
        return render(request, 'lawsuit/instancias.html', {'instances': instances_list})


def delete_instance(request, id_instance):

    try:
        Instance.objects.filter(id=id_instance).delete()
        messages.add_message(request,messages.INFO,"Instância apagada com sucesso.")
        return HttpResponseRedirect('/processos/instancias/')

    except:
        messages.add_message("Erro ao apagar instância.")
        TemplateResponse('lawsuit/instancias.html', {'message': 'Erro ao apagar instância.', })
        return HttpResponseRedirect('/processos/instancias/')


def nova_instancia(request):

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
                messages.add_message(request, messages.ERROR, "Dados salvos com sucesso.")

            except:
                messages.add_message(request,messages.ERROR,"Ocorreram erros de validação no formulário.")
        else:
            messages.add_message(request, messages.ERROR, "Ocorreram erros de validação no formulário.")

        return HttpResponseRedirect('/processos/instancias/')

    else:
        form = InstanceForm()
        return render(request,'lawsuit/nova_instancia.html',{'form':form,
                                                      'title_page': 'Instâncias - Easy Lawyer'  })



