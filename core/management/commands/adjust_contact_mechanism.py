from django.core.management.base import BaseCommand
from core.models import ContactMechanism
from django.db.models import Q


class Command(BaseCommand):
	help = ('Create groups and associate the task model permissions with them.')

	def handle(self, *args, **options):
		print('{} Mecanismos de contato existentes na base de dados'.format(ContactMechanism.objects.count()))
		ContactMechanism.objects.filter(contact_mechanism_type__name__iexact='telefone').delete()
		ContactMechanism.objects.filter(Q(person__is_customer=True) | Q(person__is_supplier=True)).delete()	
		for contact in ContactMechanism.objects.filter(
				contact_mechanism_type__name__in=['E-mail' 'email']):			
			if contact.description.split('@')[-1] != 'mtostes.com.br':
				contact.delete()
		print ('{0} Mecanismos de contato restantes'.format(ContactMechanism.objects.count()))          