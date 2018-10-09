from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from model_mommy import mommy

from task.models import Ecm, Task
from task.signals import ecm_task_post_save


User = get_user_model()


class TaskSignalsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='username')
        self.task = mommy.make(Task)

    @patch('advwin_models.tasks.export_ecm.delay')
    def test_export_ecm_signal(self, export_ecm_mock):
        # Calls only upon creation and no legacy
        ecm = Ecm(path='ECM/document.pdf',
                  create_user=self.user,
                  task=self.task)
        ecm.save()
        export_ecm_mock.assert_called_with(ecm.id)

        # Doesn't call if editing existing object
        self.assertTrue(export_ecm_mock.called)

    @patch('advwin_models.tasks.export_ecm.delay')
    def test_export_ecm_signal_legacy_code(self, export_ecm_mock):
        ecm = Ecm.objects.create(path='ECM/document.pdf',
                                 legacy_code='123',
                                 create_user=self.user,
                                 task=self.task)

        # Doesn't call if have legacy_code
        ecm_task_post_save(Ecm, ecm, created=True)
        export_ecm_mock.assert_not_called()
