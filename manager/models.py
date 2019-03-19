import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from enum import Enum

from .schemas import PARAMETERS


class TypeTemplate(Enum):
    BOOLEAN = 'Boleano'
    SIMPLE_TEXT = 'Texto Simples'
    LONG_TEXT = 'Texto'
    FOREIGN_KEY = 'Chave estrangeira'
    INTEGER = 'Inteiro'
    DECIMAL = 'Decimal'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class Template(models.Model):
    name = models.CharField(verbose_name='Nome',
                            null=False,
                            blank=False,
                            max_length=255)
    description = models.TextField(verbose_name='Descrição',
                                   null=True,
                                   blank=True)
    type = models.CharField(null=False,
                            blank=False,
                            verbose_name='Tipo',
                            max_length=15,
                            choices=TypeTemplate.choices())
    parameters = JSONField(
        null=True,
        blank=True,
        verbose_name='Características disponíveis',
        default=json.dumps(PARAMETERS, indent=4))

    class Meta:
        ordering = ('name', 'type')
        verbose_name = 'Template de configuração'
        verbose_name_plural = 'Templates de configuração'

    def __str__(self):
        return self.name
