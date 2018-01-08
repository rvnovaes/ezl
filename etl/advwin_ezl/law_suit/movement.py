from core.models import Person
from django.contrib.auth.models import User
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from etl.utils import get_users_to_import, get_message_log_default, save_error_log
from lawsuit.models import Movement, LawSuit, TypeMovement, Folder
from etl.utils import get_message_log_default, save_error_log


class MovementETL(GenericETL):
    _import_query = """
                SELECT DISTINCT
                  p.Codigo_Comp     AS folder_legacy_code,
                  pm.M_Distribuicao AS law_suit_legacy_code,
                  pm.Ident          AS legacy_code,
                  pm.Advogado       AS person_lawyer_legacy_code,
                  pm.CodMov         AS type_movement_legacy_code
                from Jurid_ProcMov AS pm
                INNER JOIN Jurid_Pastas as p on
                  p.Codigo_Comp = pm.Codigo_Comp
                INNER JOIN Jurid_agenda_table as a ON
                  pm.Ident = a.Mov
                LEFT JOIN Jurid_CodMov as cm ON
                  a.CodMov = cm.Codigo
                WHERE
                  cm.UsarOS = 1 and
                  (p.Status = 'Ativa' OR p.Status = 'Especial') AND
                  ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                  (a.SubStatus = 80)) AND a.Status = '0' -- STATUS ATIVO
                  AND a.Advogado IN ('{}')
                  """

    model = Movement
    advwin_table = "Jurid_ProcMov"
    has_status = True

    @property
    def import_query(self):
        return self._import_query.format("','".join(get_users_to_import()))

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        for row in rows:
            rows_count -= 1

            try:
                legacy_code = row['legacy_code']
                law_suit_legacy_code = row['law_suit_legacy_code']
                person_lawyer_legacy_code = row['person_lawyer_legacy_code']
                type_movement_legacy_code = row['type_movement_legacy_code']
                folder_legacy_code = row['folder_legacy_code']

                movement = self.model.objects.filter(legacy_code=legacy_code,
                                                     system_prefix=LegacySystem.ADVWIN.value).first()

                if law_suit_legacy_code:
                    lawsuit = LawSuit.objects.filter(
                        legacy_code=law_suit_legacy_code).first() or InvalidObjectFactory.get_invalid_model(LawSuit)
                else:
                    lawsuit = None
                    if LawSuit.objects.filter(folder__legacy_code=folder_legacy_code).first():
                        lawsuit = InvalidObjectFactory.get_invalid_model(LawSuit)

                type_movement = TypeMovement.objects.filter(
                    legacy_code=type_movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(TypeMovement)

                person_lawyer = Person.objects.filter(
                    legacy_code=person_lawyer_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)

                folder = Folder.objects.filter(
                    legacy_code=folder_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)

                # Conforme descrico no caso 0000486, nao existe person_lawyer na classe Movement, pois segundo analise da
                # regra de negocios, identificou-se que o usuario que cria a movimentacao e o advogado
                create_user = person_lawyer.auth_user or InvalidObjectFactory.get_invalid_model(User)

                if movement:
                    movement.law_suit = lawsuit
                    movement.folder = folder
                    movement.type_movement = type_movement
                    movement.alter_user = create_user
                    movement.is_active = True
                    movement.office = default_office
                    movement.save(update_fields=['is_active',
                                                 'law_suit',
                                                 'folder',
                                                 'type_movement',
                                                 'alter_user',
                                                 'alter_date',
                                                 'office',
                                                 ])
                else:
                    self.model.objects.create(legacy_code=legacy_code,
                                              system_prefix=LegacySystem.ADVWIN.value,
                                              alter_user=create_user,
                                              create_user=create_user,
                                              is_active=True,
                                              law_suit=lawsuit,
                                              folder=folder,
                                              type_movement=type_movement,
                                              office=default_office
                                              )
                self.debug_logger.debug(
                    "Movimentacao,%s,%s,%s,%s,%s,%s,%s,%s" % (str(legacy_code), str(LegacySystem.ADVWIN.value), str(create_user.id),
                                                    str(create_user.id),str(True),str(lawsuit.id if lawsuit else ''),str(type_movement.id),self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(msg)


if __name__ == "__main__":
    MovementETL().import_data()
