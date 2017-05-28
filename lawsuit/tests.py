from django.utils.timezone import now
from django.contrib.auth.models import User
from django.test import TestCase
from .models import TypeMovement


class TypeMovementTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='jacob', email='jacob@gmail.com', password='top_secret')
        TypeMovement.objects.create(create_user=self.user, create_date=now(), name='Audiência', legacy_code='11.02', uses_wo=True)

    def test_type_movement_uses_wo(self):
        type_movement = TypeMovement.objects.get(name='Audiência')
        self.assertTrue(type_movement.uses_wo)