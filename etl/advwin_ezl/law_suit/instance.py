# esse import deve vir antes de todos porque ele executa o __init__.py
# import os
# import sys
#
# import django
#
# sys.path.append("ezl")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
# django.setup()
from etl.advwin_ezl.advwin_ezl import GenericETL
from core.utils import LegacySystem
from lawsuit.models import Instance


class InstanceETL(GenericETL):
    import_query = """
                   SELECT Codigo, Descicao FROM Jurid_Instancia AS i1 WHERE Descicao IS NOT NULL AND Codigo =
                   (SELECT min (Codigo) FROM Jurid_Instancia AS i2 WHERE i1.Descicao = i2.Descicao)

                   """

    model = Instance
    advwin_table = 'Jurid_Instancia'
    has_status = False

    def config_import(self, rows, user, rows_count):
        for row in rows:
            code = row['Codigo']
            name = row['Descicao']

            instance = self.model.objects.filter(legacy_code=code, system_prefix=LegacySystem.ADVWIN.value).first()

            if instance:
                instance.name = name
                instance.is_active = True
                instance.alter_user = user
                instance.save(update_fields=['is_active', 'name', 'is_active', 'alter_user', 'alter_date'])

            else:
                self.model.objects.create(
                    name=name,
                    is_active=True,
                    legacy_code=code,
                    alter_user=user,
                    create_user=user,
                    system_prefix=LegacySystem.ADVWIN.value)
        super(InstanceETL, self).config_import(rows, user, rows_count)


if __name__ == "__main__":
    InstanceETL().import_data()
