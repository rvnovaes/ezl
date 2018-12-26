from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from billing.gerencianet_api import api as gn_api
from billing.models import *
# Create your views here.


class ChargeCreateView(View):
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
		payment_link = gn_api.create_payment_link(charge.charge_id)
		print(payment_link)		
		return JsonResponse({'url': payment_link.get('data').get('payment_url')})