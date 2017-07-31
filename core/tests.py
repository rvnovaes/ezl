from django.test import TestCase
from models import *
from django.core.urlresolvers import reverse
from forms import *
    
# models test
class PersonTest(TestCase):

    def create_person(self,legal_name = "Teste Unitario Usuario", 
                           name = "Teste Unitario Usuario", 
                           is_lawyer = False, 
                           is_correspondent = False, 
                           is_court = False, 
                           legal_type = 'F', 
                           cpf_cnpj = '1234567890', 
                           is_customer = False, 
                           is_supplier = False)
        return Person.objects.create(legal_name = legal_name, 
                                     name = name, 
                                     is_lawyer = is_lawyer, 
                                     is_correspondent = is_correspondent, 
                                     is_court = is_court, 
                                     legal_type = legal_type, 
                                     cpf_cnpj = cpf_cnpj, 
                                     is_customer = is_customer, 
                                     is_supplier = is_customer)

    def test_person_creation(self):
        w = self.create_whatever()
        self.assertTrue(isinstance(w, Person))
        self.assertEqual(w.__unicode__(), w.title)

