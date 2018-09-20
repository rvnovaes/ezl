from django.db import models
from core.models import AuditCreate, LegacyCode, Audit, OfficeMixin, OfficeManager
from task.models import TypeTask
import os


def get_uploda_to(instance, filename):
    path = os.path.join('media', 'ECM', str(instance.model_name), str(instance.object_id))
    if not os.path.exists(path):
        os.makedirs(path)
    return 'ECM/{0}/{1}/{2}'.format(instance.model_name, instance.object_id, filename)


class Attachment(AuditCreate, LegacyCode):
    """
    Anexos do Sistema
    app_name:
    reg_id:
    """
    model_name = models.CharField(
        verbose_name="Model", max_length=120
    )
    object_id = models.IntegerField(
        verbose_name="ID do Registro", db_index=True
    )
    file = models.FileField(
        verbose_name="Arquivo", upload_to=get_uploda_to
    )
    size = models.PositiveIntegerField(null=True, blank=True)
    exibition_name = models.CharField(
        verbose_name="Nome de Exibição", max_length=255
    )

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return '{}/{}: {}'.format(
            self.object_id, self.model_name, self.filename
        )

    def save(self, *args, **kwargs):
        if not self.size:
            try:
                self.size = self.file.size
            except:
                # Skip errors when file does not exists
                pass
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"


class DefaultAttachmentRule (Audit, OfficeMixin):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Nome')
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

    objects = OfficeManager()

    class Meta:
        ordering = ['-id']
        verbose_name = "Regra de Anexo Padrão"
        verbose_name_plural = "Regras de Anexo Padrão"
        unique_together = (('name', 'office'),)

    def __str__(self):
        return '{}:{}'.format(
            self.name, self.description
        )

    @property
    def upload_required(self):
        return True
