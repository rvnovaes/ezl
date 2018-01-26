from django.db import models
from core.models import AuditCreate, LegacyCode, Audit, OfficeMixin
from task.models import TypeTask
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


class DefaultAttachmentRule (Audit, OfficeMixin):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, verbose_name='Descrição')
    type_task = models.ForeignKey('task.TypeTask', on_delete=models.PROTECT, blank=True, null=True,
                                  verbose_name='Tipo de Serviço')
    person_customer = models.ForeignKey('core.Person', on_delete=models.PROTECT, blank=True, null=True,
                                        related_name='%(class)s_customer',
                                        verbose_name='Cliente')
    court_district = models.ForeignKey('lawsuit.CourtDistrict', on_delete=models.PROTECT,
                                       blank=True, null=True,
                                       verbose_name='Comarca')
    state = models.ForeignKey('core.State', on_delete=models.PROTECT, blank=True, null=True,
                              verbose_name="Estado")
    city = models.ForeignKey('core.City', on_delete=models.PROTECT, blank=True, null=True,
                              verbose_name="Cidade")

    class Meta:
        ordering = ['-id']
        verbose_name = "Regra de Anexo Padrão"
        verbose_name_plural = "Regras de Anexo Padrão"

    def __str__(self):
        return '{}:{}'.format(
            self.name, self.description
        )