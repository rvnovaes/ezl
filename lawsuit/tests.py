from django.utils.timezone import now
from django.contrib.auth.models import User
from django.test import TestCase
from .models import *
from .views import *
from .forms import *
from model_mommy import mommy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from core.models import Person, State
import datetime

#TODO LawSuit, Views

#Status 200: conseguiu acessar a pagina
#Status 300: Redirecionamento
#Status 404: Nao encontrado      
#model_mommy serve apenas para testes em modelos. Testes na view tem que ser feitos da maneira convencional  

class LawSuitTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')

        
    def test_routine(self):

        c_inst = mommy.make(LawSuit)                    
        self.assertTrue(isinstance(c_inst, LawSuit))

    def test_valid_LawSuitForm(self):
    
        person_lawyer = mommy.make(Person,name= 'Adv',is_lawyer = True, is_active=True).id
        folder = mommy.make(Folder).id
        instance = mommy.make(Instance).id
        court_district = mommy.make(CourtDistrict).id
        person_court = mommy.make(Person,name= 'Court',is_active=True, is_court = True).id
        court_division = mommy.make(CourtDivision,is_active=True).id
        law_suit_number = '12345'
        
        data = {'person_lawyer':person_lawyer,
                'folder':folder,
                'instance':instance,
                'court_district':court_district,
                'person_court':person_court,
                'court_division':court_division,
                'law_suit_number':law_suit_number}
                
        form = LawSuitForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
          
    def test_list_view(self):
    
        
        url = reverse('lawsuit_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        
        url = reverse('lawsuit_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        c_inst = mommy.make(LawSuit)
        url = reverse('lawsuit_update',kwargs={'pk':c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)        

      
class InstanceTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
  
          
        
    #Jeito antigo
    #def create_routine(self,name = 'Teste Instancia', legacy_code = '999-999-999',create_user_id=2):
        
    #    return Instance.objects.create(name = name, legacy_code = legacy_code, create_user_id = create_user_id)

    #todo teste tem que ter o prefixo test_    
    def test_routine(self):
        
        #mommy deixa as coisas bem mais faaceis
        c_inst = mommy.make(Instance,name='Random')
        self.assertTrue(isinstance(c_inst, Instance))

    def test_valid_InstanceForm(self):
    
        name = 'Tipo_Instacia_BLABLABLA'
        
        data = {'name': name}
        form = InstanceForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())   
        
    def test_list_view(self):
    
        
        url = reverse('instance_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        
        url = reverse('instance_create')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        c_inst = mommy.make(Instance,name='123')
        url = reverse('instance_update',kwargs={'pk':c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
    
        
    #def test_delete_view(self):
    
    #    c_inst = mommy.make(Instance,name='123')
    #    url = reverse('instance_delete',kwargs={'pk':c_inst.id})
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)
    

class FolderTest(TestCase):

     
    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')  
        self.c_inst = mommy.make(Folder)
     
    def test_routine(self):
        
        
        self.assertTrue(isinstance(self.c_inst, Folder))

    def test_valid_FolderForm(self):
    
        legacy_code = '9999'
        person_customer = mommy.make(Person,name='Joao',is_active=True).id

        data = {'legacy_code': legacy_code, 
                'person_customer':person_customer}
        form = FolderForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
    
    def test_list_view(self):
    
        
        url = reverse('folder_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        
        url = reverse('folder_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        
        url = reverse('folder_update',kwargs={'pk':self.c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    #def test_delete_view(self):
    
        
    #    url = reverse('folder_delete')
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)


class CourtDivisionTest(TestCase):

             
    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')          
        self.c_inst = mommy.make(CourtDivision)     
             
    def test_routine(self):
        
        self.assertTrue(isinstance(self.c_inst, CourtDivision))

    def test_valid_CourtDivisionForm(self):
    
        legacy_code = '9999'
        name = 'Test123'

        data = {'name': name, 'legacy_code': legacy_code}
        
        form = CourtDivisionForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_list_view(self):
    
        url = reverse('courtdivision_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    

        url = reverse('courtdivision_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        url = reverse('courtdivision_update',kwargs={'pk':self.c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    #def test_delete_view(self):
    
    #    url = reverse('courtdivision_delete')
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)


class CourtDistrictTest(TestCase):


    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
        self.c_inst = mommy.make(CourtDistrict)
    
    def test_routine(self):
        
        self.assertTrue(isinstance(self.c_inst, CourtDistrict))

    def test_valid_CourtDistrictForm(self):
    
        state = mommy.make(State,is_active=True).id
        name = 'Test123'
        
        data = {'name': name, 'state': state}
        form = CourtDistrictForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_list_view(self):
    
        url = reverse('courtdistrict_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        url = reverse('courtdistrict_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    

        url = reverse('courtdistrict_update',kwargs={'pk':self.c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    #def test_delete_view(self):
    
    #    url = reverse('courtdistrict_delete')
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)


class MovementTest(TestCase):


    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
        #self.c_inst = mommy.make(Movement)
              
    def test_routine(self):

        c_inst = mommy.make(Movement)
        self.assertTrue(isinstance(c_inst, Movement))
     
  
    def test_valid_MovementForm(self):

        legacy_code = '9999'
        person_lawyer = mommy.make(Person,is_active=True,is_lawyer=True).id
        
        law_suit = mommy.make(LawSuit,is_active=True).id
        type_movement = mommy.make(TypeMovement,is_active=True).id
        deadline = datetime.date.today()

        data = {'legacy_code': legacy_code, 
                'person_lawyer': person_lawyer, 
                'law_suit': law_suit, 
                'type_movement': type_movement, 
                'deadline': deadline}
                
        form = MovementForm(data=data)
        print(form.errors)

        self.assertTrue(form.is_valid())

    def test_list_view(self):
    
        url = reverse('movement_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        url = reverse('movement_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        c_inst = mommy.make(Movement)
        url = reverse('movement_update',kwargs={'pk':c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    #def test_delete_view(self):
    
    #    url = reverse('movement_delete')
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)

        
class TypeMovementTest(TestCase):
        
    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
        self.c_inst = mommy.make(TypeMovement,name='RandomTM')   
   
    def test_routine(self):
        self.assertTrue(isinstance(self.c_inst, TypeMovement))
        
    #TODO Testar os Forms
    def test_valid_TypeMovementForm(self):

        #Diferente do que manda o tutorial realpython, nao se deve criar uma instancia para testar o form
        name = 'Tipo_Movimentacao_BLABLABLA'
        legacy_code = '9999'
        uses_wo = True
        

        data = {'name': name, 'uses_wo': uses_wo, 'legacy_code': legacy_code}
        form = TypeMovementForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
        
    def test_list_view(self):
    
        url = reverse('type_movement_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
        
    def test_create_view(self):
    
        url = reverse('type_movement_add')
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        url = reverse('type_movement_update',kwargs={'pk':self.c_inst.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        
    #def test_delete_view(self):
    
    #    url = reverse('type_movement_delete')
    #    resp = self.client.get(url)
        
    #    self.assertEqual(resp.status_code, 200)



