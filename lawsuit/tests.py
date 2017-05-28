from django.test import TestCase
from .models import TypeMovement


class TypeMovementTestCase(TestCase):

    def setUp(self):
        TypeMovement.objects.create(name='Audiência', legacy_code='11.02', uses_wo=True)

    def test_type_movement_uses_wo(self):
        type_movement = TypeMovement.objects.get(name='Audiência')
        self.assertTrue(type_movement.uses_wo)