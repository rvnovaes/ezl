from django.db import models
from core.models import Audit

class DashboardETL(Audit):
    execution_date_start = models.DateTimeField(
        verbose_name='Inicio', auto_now_add=True, null=True, blank=True)
    execution_date_finish  = models.DateTimeField(
        verbose_name='Fim', null=True, blank=True, editable=False)
    name = models.CharField(verbose_name='ETL', max_length=100, editable=False)
    status = models.BooleanField(verbose_name='Status', default=True,
                                 editable=False)
    read_quantity = models.IntegerField(verbose_name='Quantidade Lida',
                                        default=0, editable=False)
    imported_quantity = models.IntegerField(verbose_name='Quantidade importada',
                                            default=0, editable=False)
    executed_query = models.TextField(verbose_name='Query executada', null=True,
                                      blank=True, editable=False)
    db_name_source = models.CharField(verbose_name='DB de origem',
                                     max_length=50, blank=True, null=True)
    db_host_source = models.CharField(verbose_name='Host do db de origem',
                                      blank=True, null=True, max_length=16)

    class Meta:
        db_table = 'dashboard_etl'
        ordering = ('-execution_date_start', )
        verbose_name = 'Dashboard ETL'
        verbose_name_plural = 'Dashboard ETL'

    def __str__(self):
        return self.name


class ErrorETL(Audit):
    log = models.ForeignKey(DashboardETL, verbose_name='Erros',
                            related_name='errors')
    error = models.TextField(verbose_name='Descrição do erro', null=True,
                             blank=True, editable=False)
