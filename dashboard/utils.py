from functools import wraps
from django.db import transaction


def no_commit(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		res = False
		with transaction.atomic():
			res = f(*args, **kwargs)
			transaction.set_rollback(True)
		return res
	return wrapper

def set_company(f):
	@wraps(f)
	def wrapper(self, obj, attr):
		try:		
			self.company = self.context.get('request').auth.application.company
		except AttributeError as e:
			pass
		finally:
			return f(self, obj, attr)
	return wrapper


@no_commit
@set_company
def exec_code(self, obj, attr):
	try:								
		exec(getattr(obj, attr))			
		return locals().get('value')
	except:
		return ''