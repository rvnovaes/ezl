import json
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from billing.gerencianet_api import api as gn_api
from billing.models import *
from core.views import CustomLoginRequiredView
# Create your views here.


class ChargeCreateView(CustomLoginRequiredView, View):
	def post(self, request, *args, **kwargs):
		name = request.POST.get('name')
		item = {
			'name': request.POST.get('name'), 
			'value': int(request.POST.get('value'))
		}	
		charge = Charge()					
		gn_response = gn_api.create_transaction([item])
		gn_charge = gn_response.get('data')
		charge.create_user = request.user
		charge.custom_id = gn_charge.get('custom_id')
		charge.charge_id = gn_charge.get('charge_id')
		charge.status = gn_charge.get('status')
		charge.created_at = gn_charge.get('created_at')
		charge.save()
		charge_item = ChargeItem()
		charge_item.create_user = request.user
		charge_item.charge = charge
		charge_item.name = item.get('name')
		charge_item.value = item.get('value')
		charge_item.amount = 1
		charge_item.save()	
		return JsonResponse({'charge_id': charge.charge_id})

class ConfirmPayment(CustomLoginRequiredView, View):
	content_type = 'application/json'
	def post(self, request, *args, **kwargs):
		body = json.loads(request.body)
		charge_id = body.get('charge_id')
		payment_token = body.get('payment_token')		
		data = body.get('data')
		res = gn_api.confirm_payment(charge_id, payment_token, data)
		return JsonResponse(res)


class DetailPayment(CustomLoginRequiredView, View):
	def get(self, request, charge_id, *args, **kwargs):
		return JsonResponse(gn_api.get_details_payment(charge_id))