# esse import deve vir antes de todos porque ele executa o __init__.py
from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from lawsuit.models import Folder


class FolderETL(GenericETL):
    advwin_table = 'Jurid_Pastas'
    model = Folder
    import_query = """
            SELECT DISTINCT
              p.Codigo_Comp AS legacy_code,
              p.Cliente,
              a.CodMov
            FROM Jurid_Pastas AS p
                  INNER JOIN Jurid_ProcMov AS pm ON
                    pm.Codigo_Comp = p.Codigo_Comp
                  INNER JOIN Jurid_agenda_table AS a ON
                    pm.Ident = a.Mov
                  INNER JOIN Jurid_CodMov AS cm ON
                    a.CodMov = cm.Codigo
            WHERE
              cm.UsarOS = 1 AND
              p.Status = 'Ativa' AND
              p.Codigo_Comp IS NOT NULL AND p.Codigo_Comp <> '' AND
              p.Cliente IS NOT NULL AND p.Cliente <> '' AND
              ((a.prazo_lido = 0 AND a.SubStatus = 30) OR (a.SubStatus = 80 AND a.Status = 0))
                  """
    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count):
        log_file = open('log_file.txt', 'w')
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                customer_code = row['Cliente']

                instance = self.model.objects.filter(legacy_code=legacy_code,
                                                     system_prefix=LegacySystem.ADVWIN.value).first()

                person_customer = Person.objects.filter(legacy_code=customer_code,
                                                        system_prefix=LegacySystem.ADVWIN.value).first()
                if person_customer:
                    if instance:
                        # use update_fields to specify which fields to save
                        # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                        instance.person_customer = person_customer
                        instance.is_active = True
                        instance.alter_user = user
                        instance.save(
                            update_fields=['person_customer',
                                           'is_active',
                                           'alter_date',
                                           'alter_user'])
                    else:
                        obj = self.model(person_customer=person_customer,
                                         is_active=True,
                                         legacy_code=legacy_code,
                                         system_prefix=LegacySystem.ADVWIN.value,
                                         create_user=user,
                                         alter_user=user)
                        obj.save()

                    super(FolderETL, self).config_import(rows, user, rows_count)

                self.debug_logger.debug("Pastas,%s,%s,%s,%s,%s,%s,%s"%(str(person_customer.id),str(True),str(legacy_code),
                                                                str(LegacySystem.ADVWIN.value),str(user.id),str(user.id),
                                                                self.timestr))
            except Exception as e:
                self.error_logger.error(
                    "Ocorreu o seguinte erro na importacao de Pastas: " + str(rows_count) + "," + str(
                        e) + "," + self.timestr)


if __name__ == "__main__":
    FolderETL().import_data()
