import json
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from billing.gerencianet_api import api as gn_api
from billing.models import *
from task.models import Task
from core.models import AddressType, Address
from core.views import CustomLoginRequiredView
from core.utils import get_office_session
from .forms import BillingAddressCombinedForm
from .serializers import BillingDetailSerializer


class ChargeCreateView(CustomLoginRequiredView, View):
    def post(self, request, *args, **kwargs):
        task = Task.objects.get(pk=request.POST.get('task_id'))
        name = request.POST.get('name')
        custom_id = request.POST.get('service_price_table_id')
        item = {
            'name': request.POST.get('name'),
            'value': int(request.POST.get('value')),
        }
        charge = Charge()
        gn_response = gn_api.create_transaction([item], custom_id)
        gn_charge = gn_response.get('data')
        charge.create_user = request.user
        charge.custom_id = gn_charge.get('custom_id')
        charge.charge_id = gn_charge.get('charge_id')
        charge.status = gn_charge.get('status')
        charge.created_at = gn_charge.get('created_at')
        charge.save()
        charge.task_set.add(task)
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


class BillingDetailDataView(CustomLoginRequiredView, View):
    def get(self, request, pk, *args, **kwargs):
        billing_detail = BillingDetails.objects.get(pk=pk)
        billing_serializer = BillingDetailSerializer(billing_detail)
        return JsonResponse(billing_serializer.data)


class BillingDetailBaseView(object):
    def __init__(self):
        self.office = None
        self.address = None

    def create_update_address(self, address, form):
        address.address_type = form.cleaned_data['address_type']
        address.street = form.cleaned_data['street']
        address.number = form.cleaned_data['number']
        address.complement = form.cleaned_data['complement']
        address.city_region = form.cleaned_data['city_region']
        address.zip_code = form.cleaned_data['zip_code']
        address.city = form.cleaned_data['city']
        address.state = address.city.state
        address.country = address.state.country
        address.create_user = self.request.user
        address.save()
        self.address = address

    def create_update_billing_detail(self, billing_detail, form):
        billing_detail.card_name = form.cleaned_data['card_name']
        billing_detail.email = form.cleaned_data['email']
        billing_detail.cpf_cnpj = form.cleaned_data['cpf_cnpj']
        billing_detail.birth_date = form.cleaned_data['birth_date']
        billing_detail.phone_number = form.cleaned_data['phone_number']
        billing_detail.billing_address = self.address
        billing_detail.office = self.office
        billing_detail.create_user = self.request.user
        billing_detail.save()


class BillingDetailAjaxUpdate(CustomLoginRequiredView, View, BillingDetailBaseView):
    def post(self, request, *args, **kwargs):
        self.office = get_office_session(request)
        data = {k: v for k, v in request.POST.items()}
        data['address_type'] = AddressType.objects.filter(name='Comercial').first().id
        form = BillingAddressCombinedForm(data)
        import pdb;pdb.set_trace()
        instance = BillingDetails.objects.filter(pk=kwargs.get('pk')).first()
        if form.is_valid() and instance:
            # salva o endereço
            address = instance.billing_address
            self.create_update_address(address, form)

            # salva o billing detail usando o endereço informado
            billing_detail = instance
            self.create_update_billing_detail(billing_detail, form)

            return JsonResponse({'billing_detail_id': billing_detail.id,
                                 'action': 'atualizado'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=500)


class BillingDetailAjaxCreate(CustomLoginRequiredView, View, BillingDetailBaseView):
    def post(self, request, *args, **kwargs):
        self.office = get_office_session(request)
        data = {k: v for k, v in request.POST.items()}
        data['address_type'] = AddressType.objects.filter(name='Comercial').first().id
        form = BillingAddressCombinedForm(data)
        if form.is_valid():
            # salva o endereço
            address = Address()
            self.create_update_address(address, form)

            # salva o billing detail usando o endereço informado
            billing_detail = BillingDetails()
            self.create_update_billing_detail(billing_detail, form)

            return JsonResponse({'billing_detail_id': billing_detail.id,
                                 'action': 'criado'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=500)


class BillingDetailAjaxDelete(View):
    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('ids[]')
        BillingDetails.objects.filter(pk__in=ids).delete()
        return JsonResponse({'status': 'ok'})
