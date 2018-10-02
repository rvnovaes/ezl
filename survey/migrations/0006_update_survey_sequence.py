# -*- coding: utf-8 -*-
# Created by Tiago Gomes on 2018-09-14 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_auto_20180831_1803'),
    ]

    operations = [
        migrations.RunSQL("BEGIN;"),
        migrations.RunSQL(
            "SELECT setval(pg_get_serial_sequence('\"survey_survey\"','id'), coalesce(max(\"id\"), 1), max(\"id\") IS NOT null) FROM \"survey_survey\";"
        ),
        migrations.RunSQL("COMMIT;"),
    ]
