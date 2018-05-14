# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def create_office_ezlog(apps, schema_editor):
	from core.models import Office
	from django.contrib.auth.models import User

	user = User.objects.get(username='admin')	
	office = Office()
	office.name = 'EZLog'
	office.legal_name = 'EZLog'
	office.public_office = True
	office.create_user = user
	office.save()
	office.officemembership_set.create(person=user.person, create_user=user)


class Migration(migrations.Migration):
	dependencies = [
		('core', '0077_office_public_office'), 
	]

	operations = [
		migrations.RunPython(create_office_ezlog), 
	]
