import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from enum import Enum

from .schemas import DEFAULT_VALUE
from core.models import Audit, OfficeMixin, OfficeManager
from financial.utils import remove_special_char


class TypeTemplate(Enum):
    BOOLEAN = 'Boleano'
    SIMPLE_TEXT = 'Texto Simples'
    LONG_TEXT = 'Texto Longo'
    FOREIGN_KEY = 'Chave estrangeira'
    INTEGER = 'Inteiro'
    DECIMAL = 'Decimal'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        choices = [(x.name, x.value) for x in cls]
        choices.sort(key=lambda tup: tup[1])
        return choices


class Template(Audit):
    name = models.CharField(verbose_name='Nome',
                            null=False,
                            blank=False,
                            max_length=255)
    template_key = models.CharField(verbose_name='Chave',
                                    null=False,
                                    blank=False,
                                    max_length=255,
                                    unique=True)
    description = models.TextField(verbose_name='Descrição',
                                   null=True,
                                   blank=True)
    type = models.CharField(null=False,
                            blank=False,
                            verbose_name='Tipo',
                            max_length=15,
                            choices=TypeTemplate.choices())
    parameters = JSONField(
        null=False,
        blank=False,
        verbose_name='Características disponíveis',)

    class Meta:
        ordering = ('name', 'type')
        verbose_name = 'Template de configuração'
        verbose_name_plural = 'Templates de configuração'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.template_key:
            self.template_key = remove_special_char(self.name).strip().lower().replace(' ', '_')
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class TemplateValue(OfficeMixin, Audit):

    template = models.ForeignKey(Template, verbose_name='Configuração')
    value = JSONField(
        null=True,
        blank=True,
        verbose_name='Valor',
        default=json.dumps(DEFAULT_VALUE, indent=4))

    objects = OfficeManager()

    class Meta:
        ordering = ('office', 'template')
        verbose_name = 'Configuração por escritório'
        verbose_name_plural = 'Configurações por escritório'

    @property
    def use_upload(self):
        return False
