# esse import deve vir antes de todos porque ele executa o __init__.py
from core.models import Person
from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL
from lawsuit.models import LawSuit, Folder, Instance, CourtDistrict, CourtDivision


class LawsuitETL(GenericETL):
    model = LawSuit
    advwin_table = 'Jurid_Pastas'

    query = "SELECT p1.Advogado AS person_legacy_code, " \
            " p1.Codigo_Comp AS legacy_code,   " \
            " p1.Instancia AS instance_legacy_cod,  " \
            " p1.Comarca AS court_district_legacy_code," \
            " p1.Tribunal AS person_court_legacy_code,  " \
            " p1.Varas AS court_division_legacy_code," \
            " p1.NumPrc1 AS law_suit_number" \
            " FROM Jurid_Pastas AS p1 " \
            " WHERE   p1.Status = 'Ativa' " \
            " AND   p1.Dt_Saida IS NULL  " \
            " AND   p1.NumPrc1 IS NOT NULL  " \
            " AND p1.NumPrc1 <> '' " \
            " AND   p1.Codigo_Comp IS NOT NULL " \
            " AND p1.Codigo_Comp <> ''"

    has_status = True

    def load_etl(self, rows, user):
        for row in rows:

            person_legacy_code = row['person_legacy_code']
            legacy_code = row['legacy_code']
            instance_legacy_cod = row['instance_legacy_cod']
            court_district_legacy_code = row['court_district_legacy_code']
            person_court_legacy_code = row['person_court_legacy_code']
            court_division_legacy_code = row['court_division_legacy_code']
            law_suit_number = row['law_suit_number']

            instance = self.model.objects.filter(legacy_code=legacy_code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()
            folder = Folder.objects.filter(legacy_code=legacy_code).first()
            person_lawyer = Person.objects.filter(legacy_code=person_legacy_code).first()  # advogado burro
            instance_lawsuit = Instance.objects.filter(legacy_code=instance_legacy_cod).first()
            court_district = CourtDistrict.objects.filter(name=court_district_legacy_code).first()  # court_district
            person_court = Person.objects.filter(legacy_code=person_court_legacy_code).first()  # campo donkey
            court_division = CourtDivision.objects.filter(legacy_code=court_division_legacy_code).first()

            if folder and person_lawyer and instance_lawsuit and court_district and person_court and court_division:
                print(row)
                if instance:
                    instance.folder = folder
                    instance.person_lawyer = person_lawyer
                    instance.instance = instance_lawsuit
                    instance.court_district = court_district
                    instance.court_division = court_division
                    instance.person_court = person_court
                    instance.law_suit_number = law_suit_number
                    instance.is_active = True
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    instance.save(
                        update_fields=[
                            'is_active',
                            'folder',
                            'person_lawyer',
                            'instance',
                            'court_district',
                            'court_division',
                            'person_court',
                            'law_suit_number',
                            'alter_user',
                            'alter_date']
                    )
                else:
                    self.model.objects.create(
                        folder=folder,
                        person_lawyer=person_lawyer,
                        instance=instance_lawsuit,
                        court_district=court_district,
                        court_division=court_division,
                        person_court=person_court,
                        law_suit_number=law_suit_number,
                        alter_user=user,
                        create_user=user,
                        is_active=True,
                        legacy_code=legacy_code,
                        system_prefix=LegacySystem.ADVWIN.value)

            super(LawsuitETL, self).load_etl(rows, user)


if __name__ == "__main__":
    LawsuitETL().import_data()
