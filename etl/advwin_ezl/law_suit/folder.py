# esse import deve vir antes de todos porque ele executa o __init__.py
from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import Folder
from etl.utils import get_message_log_default, save_error_log, get_clients_to_import
from financial.models import CostCenter


class FolderETL(GenericETL):
    advwin_table = 'Jurid_Pastas'
    model = Folder
    _import_query = """
            SELECT DISTINCT
              p.Codigo_Comp AS legacy_code,
              p.Cliente,
              p.Setor
            FROM Jurid_Pastas AS p
                  LEFT JOIN Jurid_ProcMov AS pm ON
                    pm.Codigo_Comp = p.Codigo_Comp
                  INNER JOIN Jurid_agenda_table AS a ON
                    a.Pasta = p.Codigo_Comp
                  INNER JOIN Jurid_CodMov AS cm ON
                    a.CodMov = cm.Codigo
            WHERE
              cm.UsarOS = 1 AND
              (p.Status = 'Ativa' OR p.Status = 'Especial') AND
              p.Codigo_Comp IS NOT NULL AND p.Codigo_Comp <> '' AND
              p.Cliente IS NOT NULL AND p.Cliente <> '' AND
                    a.Ident IN (2622474	,
								2473981	,
								2303529	,
								2391979	,
								2381056	,
								2264799	,
								2251917	,
								2369180	,
								2622910	,
								2733154	,
								2519977	,
								2623158	,
								2989869	,
								2004275	,
								1899787	
								)
                  """
    has_status = True

    @property
    def import_query(self):
        return self._import_query.format(
            cliente="','".join(get_clients_to_import()))

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        invalid_cost_center = InvalidObjectFactory.get_invalid_model(
            CostCenter)
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                customer_code = row['Cliente']
                cost_center = row['Setor'].strip()
                cost_center_instance = invalid_cost_center

                if cost_center:
                    try:
                        cost_center_instance = CostCenter.objects.get(
                            system_prefix=LegacySystem.ADVWIN.value,
                            legacy_code=cost_center)
                    except CostCenter.DoesNotExist:
                        pass

                instance = self.model.objects.filter(
                    legacy_code=legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()

                person_customer = Person.objects.filter(
                    legacy_code=customer_code,
                    legacy_code__isnull=False,
                    offices=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()

                if person_customer:
                    if instance:
                        # use update_fields to specify which fields to save
                        # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                        instance.person_customer = person_customer
                        instance.is_active = True
                        instance.alter_user = user
                        instance.cost_center = cost_center_instance
                        instance.office = default_office
                        instance.save(update_fields=[
                            'person_customer', 'is_active', 'alter_date',
                            'alter_user', 'cost_center', 'office'
                        ])
                    else:
                        obj = self.model(
                            person_customer=person_customer,
                            is_active=True,
                            legacy_code=legacy_code,
                            system_prefix=LegacySystem.ADVWIN.value,
                            create_user=user,
                            cost_center=cost_center_instance,
                            alter_user=user,
                            office=default_office)
                        obj.save()

                self.debug_logger.debug(
                    "Pastas,%s,%s,%s,%s,%s,%s,%s"
                    % (str(person_customer.id), str(True), str(legacy_code),
                       str(LegacySystem.ADVWIN.value), str(user.id),
                       str(user.id), self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e)
                save_error_log(log, user, msg)


if __name__ == "__main__":
    FolderETL().import_data()
