from django.utils.timezone import now
from django.contrib.auth.models import User
from django.test import TestCase
from .models import *
from .views import *
from .forms import *
from lawsuit.models import Movement
from core.models import Person
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
    
    #def test_update_view(self):
    
    #    c_inst = mommy.make(TypeTask)
    #    url = reverse('typetask_update',kwargs={'pk':c_inst.__str__})
    #    resp = self.client.get(url)    

class TaskTest(TestCase):

    def setUp(self):
        
        user = User.objects.create_user(username='username', password='password')
        self.client.login(username='username', password='password')
        #self.c_inst = mommy.make(Instance,name='Random')    

    def test_model(self):
        
        #mommy deixa as coisas bem mais faaceis
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
    
        url = reverse('task_add')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
    
    #def test_update_view(self):
    
    #    c_inst = mommy.make(Task)
    #    url = reverse('task_update',kwargs={'pk':c_inst.id})
    #    resp = self.client.get(url)


class TaskHistoryTest(TestCase):

    def test_model(self):
        
        #mommy deixa as coisas bem mais faaceis
        c_inst = mommy.make(TaskHistory)
        self.assertTrue(isinstance(c_inst, TaskHistory))
        
class EcmTest(TestCase):

    def test_model(self):
        
        #mommy deixa as coisas bem mais faaceis
        c_inst = mommy.make(Ecm)
        self.assertTrue(isinstance(c_inst, Ecm)) #Para fazer esse test e preciso criar uma pasta em /opt/files_easy_lawyer com permissao para escrita
        
    def test_valid_EcmForm(self):
    
        task = mommy.make(Task).id
        file_path = 'arquivo_exemplo.txt' #tem que ta na pasta raiz
        #print ("Existe arquivo",os.path.isfile(file_path))
        path = SimpleUploadedFile(name=file_path, content=open(file_path, 'rb').read())
        data = {'task':task}
        file_dict = {'path':path}
        form = EcmForm(data=data,files=file_dict) #ATENCAO!!!!!!!!! ARQUIVO SE PASSA PELO PARAMETRO "files" (oh god D:)
        print(form.errors)
        self.assertTrue(form.is_valid())    
        
        
        
