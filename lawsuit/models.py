from django.db import models
from core.models import Audit
# Create your models here.
class TypeMovement(Audit):
    name = models.CharField(max_length=255,blank=False,null=False)
    legacy_code = models.CharField(max_length=255)
    uses_wo = models.BooleanField(null=False, default=False)

    class Meta:
        db_table = "type_movement"
    def __str__(self):
        return self.name

