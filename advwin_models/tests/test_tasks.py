from json import dumps
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from model_mommy import mommy

from advwin_models.tasks import export_task, get_task_observation, TaskObservation
from task.models import Task, TaskStatus, SurveyType, TypeTask


User = get_user_model()


class TasksTest(TestCase):

    @patch('advwin_models.advwin.JuridFMAudienciaCorrespondente.__table__.insert')
    @patch('advwin_models.tasks.update_advwin_task')
    def test_export_task(self, update_advwin_task_mock, table_insert_mock):
        # User.objects.create(username='username')

        type_task = mommy.make(TypeTask,
                               name='TypeTask',
                               survey_type=SurveyType.COURTHEARING.name.title())
        task = mommy.make(Task,
                          legacy_code='1A2B3C',
                          task_status=TaskStatus.DONE,
                          type_task=type_task,
                          survey_result=dumps({'agenda_id': 1, 'versao': 1, 'question1': 1}))

        export_task(task.id, task)

        update_advwin_task_mock.assert_called_with(
            task,
            {
                'SubStatus': 70,
                'Status': 2,
                'Data_Fech': task.execution_date,
                'prazo_lido': 1,
                'Prazo_Interm': 1,
                'Ag_StatusExecucao': '',
                'Data_cumprimento': task.execution_date,
                'Obs': get_task_observation(task, TaskObservation.DONE.value, 'execution_date'),
            },
            True)

        table_insert_mock.assert_called_with()

        table_insert_mock.return_value.values.assert_called_with(agenda_id=task.legacy_code,
                                                                 versao=1)
