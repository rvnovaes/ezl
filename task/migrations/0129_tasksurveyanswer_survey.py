# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-07 12:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def update_survey(apps, schema_editor):
    TaskSurveyAnswer = apps.get_model('task', 'TaskSurveyAnswer')
    survey_id_list = list(set(TaskSurveyAnswer.objects.all().values_list('task__type_task__survey', flat=True)))
    for survey_id in survey_id_list:
        TaskSurveyAnswer.objects.filter(task__type_task__survey=survey_id).update(survey_id=survey_id)


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_update_survey_sequence'),
        ('task', '0128_migrate_survey_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksurveyanswer',
            name='survey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Survey'),
        ),
        migrations.RunPython(update_survey),
    ]
