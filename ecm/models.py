from django.db import models
from core.models import AuditCreate, LegacyCode
import os


def get_uploda_to(instance, filename):
    path = os.path.join('media', 'ECM', 'attachment')
    if not os.path.exists(path):
        os.makedirs(path)
    return f'ECM/attachment/{filename}'


class Attachment(AuditCreate, LegacyCode):
    """
    Anexos do Sistema
    app_name:
    repr_name:
    reg_id:
    """
    model_name = models.CharField(
        verbose_name="Model", max_length=120
    )
    object_id = models.PositiveSmallIntegerField(
        verbose_name="ID do Registro", db_index=True
    )
    file = models.FileField(
        verbose_name="Arquivo", upload_to=get_uploda_to
    )

    class Meta:
        ordering = ['-id']
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return '{}/{}: {}'.format(
            self.object_id, self.model_name, self.filename
        )