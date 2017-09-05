from django.utils.timezone import now
from django.contrib.auth.models import User
from django.test import TestCase
from .models import *
from .views import *
from .forms import *
from lawsuit.models import Movement
from core.models import Person, ContactMechanismType
from model_mommy import mommy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class TypeTaskTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')


    def test_model(self):
        
        #mommy deixa as coisas bem mais faaceis
        c_inst = mommy.make(TypeTask)
        self.assertTrue(isinstance(c_inst, TypeTask))
        
    def test_valid_TypeTaskForm(self):
    
        #form = TypeTaskForm()
        #st = dict(form.fields['survey_type'].choices)['Diligence'] #Para charfield com choices em enum, usar as escolhas do enum em lowercase
            
        data = {'name':'Tipo1','survey_type':'Diligence'}
        form = TypeTaskForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())    
        
    def test_list_view(self):
    
        url = reverse('typetask_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
    
    def test_create_view(self):
    
        url = reverse('typetask_add')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        
    def test_update_view(self):
    
        c_inst = mommy.make(TypeTask)
        url = reverse('typetask_update',kwargs={'pk':c_inst.id})
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 200)   
    
    def test_delete_view(self):
    
        c_inst = mommy.make(TypeTask)
        data = {'typetask_list':{c_inst.id}}
        url = reverse('typetask_delete')
        resp = self.client.post(url,data,follow=True)
        #print(resp.context)
        
        self.assertEqual(resp.status_code, 200)     

class TaskTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
        #self.c_inst = mommy.make(Instance,name='Random')    

    def test_model(self):
        #mommy deixa as coisas bem mais faaceis
        mommy.make(ContactMechanismType, name='email')
        c_inst = mommy.make(Task)
        self.assertTrue(isinstance(c_inst, Task))
        
        
    def test_valid_TaskForm(self):
    
        movement = mommy.make(Movement).id
        person_common = mommy.make(Person,name='Advogado',is_active=True, is_correspondent = False).id
        person_correspondent = mommy.make(Person,name='Correspondente',is_active=True, is_correspondent = True).id
        type_task = mommy.make(TypeTask).id
        delegation_date = datetime.date.today()
        
        data = {'movement': movement,
                'person_asked_by': person_common,
                'person_executed_by': person_correspondent,
                'type_task': type_task,
                'delegation_date': delegation_date} #Unico requerido
        form = TaskForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())    

    def test_list_view(self):
    
        url = reverse('task_list')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
    
    def test_create_view(self):
        movement = mommy.make(Movement).id
        url = reverse('task_add', kwargs={'movement': movement})
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
    
    def test_update_view(self):
        #Task tem algumas fk, o que pode causar erros se instanciados diretamente pelo mommy.
        #Neste caso deve-se instanciar cada objeto separadamente
        mommy.make(ContactMechanismType, name='email')
        c_inst = mommy.make(Task, movement=mommy.make(Movement, legacy_code='999'),
                            person_asked_by=mommy.make(Person, is_active=True, is_lawyer=True),
                            person_executed_by=mommy.make(Person, is_lawyer=True),
                            type_task=mommy.make(TypeTask))
        
        print("Printou",c_inst.id)
        url = reverse('task_update', kwargs={'pk': str(c_inst.id), 'movement': c_inst.movement.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_delete_view(self):
        mommy.make(ContactMechanismType, name='email')
        c_inst = mommy.make(Task)
        data = {'task_list': {c_inst.id}}
        url = reverse('task_delete')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)


class TaskHistoryTest(TestCase):

    def test_model(self):
        
        #mommy deixa as coisas bem mais faaceis
        mommy.make(ContactMechanismType, name='email')
        c_inst = mommy.make(TaskHistory)
        self.assertTrue(isinstance(c_inst, TaskHistory))
        
class EcmTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')


    def test_model(self):
        # mommy deixa as coisas bem mais faaceis
        c_inst = mommy.make(Ecm)
        self.assertTrue(isinstance(c_inst, Ecm))  # Para fazer esse test e preciso criar uma pasta em /opt/files_easy_lawyer com permissao para escrita
        
    def test_valid_EcmForm(self):
        task = mommy.make(Task).id
        file_path = 'arquivo_exemplo.txt' #tem que ta na pasta raiz
        path = SimpleUploadedFile(name=file_path, content=open(file_path, 'rb').read())
        data = {'task':task}
        file_dict = {'path':path}
        form = EcmForm(data=data,files=file_dict) #ATENCAO!!!!!!!!! ARQUIVO SE PASSA PELO PARAMETRO "files" (oh god D:)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_create_view(self):
        task = mommy.make(Task, movement=mommy.make(Movement, legacy_code='999'),
                          person_asked_by=mommy.make(Person, name='joao', is_active=True, is_lawyer=True),
                          person_executed_by=mommy.make(Person, name='pedro', is_lawyer=True),
                          type_task=mommy.make(TypeTask, name='TT123')).id
        url = reverse('ecm_add', kwargs={'pk': task})
        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 200)
    
    def test_delete_view(self):
        task = mommy.make(Task,movement=mommy.make(Movement,legacy_code='999'),
                                 person_asked_by=mommy.make(Person,name='joao',is_active=True,is_lawyer=True),
                                 person_executed_by=mommy.make(Person,name='pedro',is_lawyer=True),
                                 type_task=mommy.make(TypeTask,name='TT123')).id       
        url = reverse('delete_ecm',kwargs={'pk':task})
        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 200)    
        
        
        
