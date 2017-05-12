from django.db import models
from core.models import Audit
# Create your models here.

class TypeMovement(Audit):
    name = models.CharField(max_length=255,blank=False,null=False,default="",unique=True)
    legacy_code = models.CharField(max_length=255,blank=False,null=False,default="",unique=True)
    uses_wo = models.BooleanField(default=True)

    class Meta:
        db_table = "type_movement"

    def __str__(self):
        return self.name

