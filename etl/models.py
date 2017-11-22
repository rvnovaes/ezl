from django.db import models
from core.models import Audit

class DashboardETL(Audit):
    execution_date_start = models.DateTimeField(
        verbose_name='Inicio', auto_now=True, null=True, blank=True)
    execution_date_finish  = models.DateTimeField(
        verbose_name='Fim', null=True, blank=True)
    name = models.CharField(verbose_name='ETL', max_length=100)

    class Meta:
        db_table = 'dashboard_etl'
        ordering = ('execution_date_finish', )
        verbose_name = 'Dashboard ETL'
        verbose_name_plural = 'Dashboard ETL'

    def __str__(self):
        return self.name
