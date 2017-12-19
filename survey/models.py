from django.db import models


class Survey(models.Model):

    type_task = models.ManyToManyField('task.TypeTask', verbose_name='Tipos de OS')
    data = models.TextField(
        verbose_name='Conteúdo',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Pesquisa'
