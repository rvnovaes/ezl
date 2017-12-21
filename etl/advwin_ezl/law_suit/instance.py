from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from core.utils import LegacySystem
from lawsuit.models import Instance
from etl.utils import get_message_log_default, save_error_log


class InstanceETL(GenericETL):
    import_query = """
                   SELECT Codigo AS legacy_code,
                          Descicao

                   FROM Jurid_Instancia AS i1

                   WHERE Descicao IS NOT NULL AND Codigo =
                   (SELECT min (Codigo)
                      FROM Jurid_Instancia AS i2
                      WHERE i1.Descicao = i2.Descicao)

                   """

    model = Instance
    advwin_table = 'Jurid_Instancia'
    has_status = False

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        for row in rows:

            try:
                code = row['legacy_code']
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

                self.debug_logger.debug(
                    "Instancias,%s,%s,%s,%s,%s,%s,%s" % (str(name), str(True), str(code),str(user.id), str(user.id),
                                                     str(LegacySystem.ADVWIN.value), self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == "__main__":
    InstanceETL().import_data()
