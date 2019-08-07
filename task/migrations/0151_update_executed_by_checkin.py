# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0150_update_task_advwin'),
    ]

    operations = []

    sql = """UPDATE 
  task t
SET 
  executed_by_checkin_id = g.id 
FROM 
  task_taskgeolocation g  
WHERE 
  t.executed_by_checkin_id is not null and
  t.id = g.task_id and 
  g.checkpointtype = 'Checkin'
  """

    operations.append(migrations.RunSQL(sql))
