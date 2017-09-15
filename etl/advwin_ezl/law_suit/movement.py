from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from etl.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import Movement, LawSuit, TypeMovement


class MovementETL(GenericETL):
    import_query = "SELECT " \
                   "pm.M_Distribuicao AS law_suit_legacy_code, " \
            "pm.Ident AS legacy_code, " \
            "pm.Advogado AS person_lawyer_legacy_code, " \
            "pm.CodMov AS type_movement_legacy_code " \
            "FROM Jurid_ProcMov AS pm " \
            "INNER JOIN Jurid_Pastas AS p " \
            "ON pm.Codigo_Comp = p.Codigo_Comp " \
            "WHERE (p.Status = 'Ativa' OR p.Dt_Saida IS NULL) " \
            " order by pm.ident  DESC "
    model = Movement
    advwin_table = "Jurid_ProcMov"
    has_status = True

    def config_import(self, rows, user, rows_count):
        for row in rows:
            print(rows_count)
            rows_count -= 1

            legacy_code = row['legacy_code']
            law_suit_legacy_code = row['law_suit_legacy_code']
            person_lawyer_legacy_code = row['person_lawyer_legacy_code']
            type_movement_legacy_code = row['type_movement_legacy_code']

            movement = self.model.objects.filter(legacy_code=legacy_code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()

            lawsuit = LawSuit.objects.filter(legacy_code=law_suit_legacy_code).first()

            type_movement = TypeMovement.objects.filter(
                legacy_code=type_movement_legacy_code).first() or InvalidObjectFactory.get_invalid_model(TypeMovement)

            person_lawyer = Person.objects.filter(
                legacy_code=person_lawyer_legacy_code).first() or InvalidObjectFactory.get_invalid_model(Person)

            if not lawsuit:
                # se não encontrou o registro, busca o registro inválido
                lawsuit = LawSuit.objects.first()
                # InvalidObjectFactory.get_invalid_model(LawSuit)

            if movement:
                movement.law_suit = lawsuit
                movement.type_movement = type_movement
                movement.person_lawyer = person_lawyer
                movement.is_active = True
                movement.save(update_fields=['is_active',
                                             'law_suit',
                                             'type_movement',
                                             'person_lawyer',
                                             'alter_user',
                                             'alter_date',
                                             ])
            else:
                self.model.objects.create(legacy_code=legacy_code,
                                          system_prefix=LegacySystem.ADVWIN.value,
                                          alter_user=user,
                                          create_user=user,
                                          is_active=True,
                                          law_suit=lawsuit,
                                          type_movement=type_movement,
                                          person_lawyer=person_lawyer
                                          )

        super(MovementETL, self).config_import(rows, user, rows_count)


if __name__ == "__main__":
    MovementETL().import_data()
