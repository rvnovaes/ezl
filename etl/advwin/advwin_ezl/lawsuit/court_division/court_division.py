from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL
from lawsuit.models import CourtDivision


class CourtDivisionETL(GenericETL):
    advwin_table = 'Jurid_Varas'
    model = CourtDivision
    query = "SELECT codigo, descricao FROM Jurid_Varas AS v1 " \
            "WHERE codigo = (SELECT min(codigo) FROM Jurid_Varas AS v2 WHERE v1.descricao = v2.descricao)"
    has_status = False

    def load_etl(self, rows, user):
        for row in rows:
            code = row['codigo']
            name = row['descricao']

            # tem que verificar se é novo antes para não salvar o create_user ao fazer update
            court_division = CourtDivision.objects.filter(legacy_code=code,
                                                          system_prefix=LegacySystem.ADVWIN.value).first()
            if court_division:

                obj = CourtDivision.objects.update(
                    name=name,
                    is_active=True,
                    alter_user=user)
            else:
                obj = CourtDivision.objects.create(name=name,
                                                   is_active=True,
                                                   legacy_code=code,
                                                   system_prefix=LegacySystem.ADVWIN.value,
                                                   create_user=user,
                                                   alter_user=user)
            # obj.save()
            super(CourtDivisionETL, self).load_etl(rows, user)


if __name__ == "__main__":
    CourtDivisionETL().import_data()
