# esse import deve vir antes de todos porque ele executa o __init__.py
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from financial.models import CostCenter
from etl.utils import get_message_log_default, save_error_log, get_clients_to_import


class CostCenterETL(GenericETL):
    advwin_table = 'Jurid_Setor'
    model = CostCenter
    import_query = """
            SELECT DISTINCT
              s.Codigo AS legacy_code,
              s.Descricao
            FROM Jurid_Setor AS s
            WHERE
              s.Ativo = 1
                  """
    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                name = row['Descricao']
                instance = self.model.objects.filter(
                    legacy_code=legacy_code,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                if instance:
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    instance.name = name
                    instance.is_active = True
                    instance.alter_user = user
                    instance.office = default_office
                    instance.save(
                        update_fields=['name',
                                       'is_active',
                                       'alter_date',
                                       'alter_user',
                                       'office'])
                else:
                    instance = self.model.objects.create(
                        name=name,
                        is_active=True,
                        legacy_code=legacy_code,
                        system_prefix=LegacySystem.ADVWIN.value,
                        create_user=user,
                        alter_user=user,
                        office=default_office)

                self.debug_logger.debug("Centro de Custo, {}, {}".format(
                    instance.id, self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name, rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == "__main__":
    CostCenterETL().import_data()
