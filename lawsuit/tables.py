import django_tables2 as tables
from .models import TypeMovement


class TypeMovementTable(tables.Table):
    model = TypeMovement
    fields = ['name', 'legacy_code', 'uses_wo']
    attrs = {"class": "table-striped table-bordered"}
    empty_text = "Não Existem Tipos de Movimentação Cadastrados"
