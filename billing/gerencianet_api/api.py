from gerencianet import Gerencianet
from django.conf import settings
import json 

def get_connection():
	return Gerencianet(settings.GERENCIANET_CREDENTIALS)

def create_transaction(items):
	gn = get_connection()
	body = {
		'items': items, 
		'metadata': {
			'notification_url':'https://webhook.site/e983e7fe-7ff4-4251-b107-97167aa139e2'
			}, 		
	}	
	return gn.create_charge(body=body)

def create_payment_link(charge_id): 
	gn = get_connection()
	params =  {
		'id': charge_id
	}
	link = {
	    'message': 'Cobrança de proviência',
	    'expire_at': '2018-12-19',
	    'request_delivery_address': False,
	    'payment_method': 'credit_card'
	}
	return gn.link_charge(params=params, body=link)


def confirm_payment(charge_id, payment_token, data):
	gn = get_connection()
	params = {
	    'id': charge_id
	}	
	body = {
	    'payment': {
	        'credit_card': {
	            'installments': int(data.get('installments')),
	            'payment_token': payment_token,
	            'billing_address': data.get('billing_address'),
	            'customer': data.get('customer')
	        }
	    }
	}	
	return gn.pay_charge(params=params, body=body)

def get_notification(token):
	gn = get_connection()
	return gn.get_notification(params={'token': token})