from django.core.management.base import BaseCommand
from task.models import Task
from advwin_models.tasks import *

def get_advwin_ecms(task_legacy_code): 
	sql = "SELECT ID_doc FROM Jurid_Ged_Main WHERE Codigo_Or = '{}'".format(task_legacy_code)
	result = get_advwin_engine().execute(sql)
	return result.fetchall()

def related_exist(folder_related, id_doc):
	sql = "SELECT * FROM Jurid_gedlig WHERE id_tabela_or = 'Pastas' and id_codigo_or = '{}' AND Id_id_doc = {}".format(folder_related, id_doc)    	
	result = get_advwin_engine().execute(sql)
	return result.fetchall()

def insert_advwin_related_folder(folder_related, id_doc):	    		
	stmt = """
		INSERT INTO Jurid_gedlig (id_tabela_or, id_codigo_or, id_id_or, Id_id_doc)
		VALUES ('Pastas','{folder_related}', 0, {id_doc}) 
	""".format(folder_related=folder_related, id_doc=id_doc)
	result = get_advwin_engine().execute(stmt)
	total_afected = result.rowcount
	print(total_afected)


class Command(BaseCommand):
	help = ('Insere o relacionamento do arquivo com a pasta no advwin')

	def add_arguments(self, parser):		
		parser.add_argument('--initial_date')
		parser.add_argument('--end_date')

	def handle(self, *args, **options):    			
		initial_date=options.get('initial_date')
		end_date=options.get('end_date')
		for task in Task.objects.filter(
				office_id=1, task_status=TaskStatus.FINISHED, finished_date__gte=initial_date, finished_date__lte=end_date):
			print(task)
			ecms = get_advwin_ecms(task.legacy_code)
			folder_related = get_folder_to_related(task)
			for ecm in ecms:
				if not related_exist(folder_related, ecm['ID_doc']):
					print('{} - nao tem relacionamento'.format(ecm['ID_doc']))
					insert_advwin_related_folder(folder_related, ecm['ID_doc'])    			
				else:
					print('{} - tem relacionamento'.format(ecm['ID_doc']))
