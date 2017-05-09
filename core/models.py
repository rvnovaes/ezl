from django.db import models
from django.conf import settings
# Create your models here.


class Audit(models.Model):
    create_date = models.DateTimeField()
    alter_date = models.DateTimeField(blank=True, null=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                       related_name='%(class)s_create_user')
    alter_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True,
                                      related_name='%(class)s_alter_user')
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
