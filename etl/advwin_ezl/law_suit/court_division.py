from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from lawsuit.models import CourtDivision
from etl.utils import get_message_log_default, save_error_log


class CourtDivisionETL(GenericETL):
    advwin_table = 'Jurid_Varas'
    model = CourtDivision
    import_query = """
                    SELECT
                      codigo AS legacy_code,
                      descricao
                    FROM Jurid_Varas AS v1
                    WHERE codigo = (SELECT min(codigo)
                                    FROM Jurid_Varas AS v2
                                    WHERE v1.descricao = v2.descricao)
                    """
    has_status = False

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        for row in rows:

            try:
                code = row['legacy_code']
                name = row['descricao']

                # tem que verificar se é novo antes para não salvar o create_user ao fazer update
                instance = self.model.objects.filter(legacy_code=code,
                                                     system_prefix=LegacySystem.ADVWIN.value).first()
                if instance:
                    instance.name = name
                    instance.alter_user = user
                    instance.is_active = True
                    instance.save(update_fields=['is_active', 'name', 'alter_user', 'alter_date'])
                else:
                    self.model.objects.create(name=name,
                                              is_active=True,
                                              legacy_code=code,
                                              system_prefix=LegacySystem.ADVWIN.value,
                                              create_user=user,
                                              alter_user=user)

                self.debug_logger.debug(
                    "Varas,%s,%s,%s,%s,%s,%s,%s" % (str(name), str(True), str(code),
                                                     str(LegacySystem.ADVWIN.value), str(user.id), str(user.id),
                                                     self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, msg)
                self.error_logger.error(msg)
                save_error_log(msg)

if __name__ == "__main__":
    CourtDivisionETL().import_data()
