# esse import deve vir antes de todos porque ele executa o __init__.py
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL

from core.models import Person
from core.utils import LegacySystem
from lawsuit.models import LawSuit, Folder, Instance, CourtDistrict, CourtDivision


class LawsuitETL(GenericETL):
    model = LawSuit
    advwin_table = 'Jurid_Pastas'

    query = "SELECT p.Advogado AS person_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Codigo)) LIKE '') or (d.D_Codigo is null) then " \
            "     p.Codigo_Comp else d.D_Codigo end as legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Codigo_Inst)) LIKE '') or (d.D_Codigo_Inst is null) then " \
            "     p.Instancia else d.D_Codigo_Inst end as instance_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Comarca)) LIKE '') or (d.D_Comarca is null) then " \
            "     p.Comarca else d.D_Comarca end as court_district_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Tribunal)) LIKE '') or (d.D_Tribunal is null) then " \
            "     p.Tribunal else d.D_Tribunal end as person_court_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Vara)) LIKE '') or (d.D_Vara is null) then " \
            "     p.Varas else d.D_Vara end as court_division_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_NumPrc)) LIKE '') or (d.D_NumPrc is null) then " \
            "     p.NumPrc1 else d.D_NumPrc end as law_suit_number " \
            " FROM Jurid_Pastas AS p " \
            " left join Jurid_Distribuicao as d on " \
            "   p.Codigo_Comp = d.Codigo_Comp " \
            " WHERE" \
            "   p.Status = 'Ativa' AND " \
            "   p.Dt_Saida IS NULL  AND" \
            "   ((p.NumPrc1 IS NOT NULL AND p.NumPrc1 <> '') or " \
            "    (d.D_NumPrc IS NOT NULL AND d.D_NumPrc <> '')) AND" \
            "   ((p.Codigo_Comp IS NOT NULL AND p.Codigo_Comp <> '') or " \
            "    (d.Codigo_Comp IS NOT NULL AND d.Codigo_Comp <> '')) AND" \
            "   ((p.Instancia IS NOT NULL AND p.Instancia <> '') or " \
            "    (d.D_Codigo_Inst IS NOT NULL AND d.D_Codigo_Inst <> '')) "

    has_status = True

    def load_etl(self, rows, user):
        for row in rows:
            print(row)

            person_legacy_code = row['person_legacy_code']
            legacy_code = row['legacy_code']
            instance_legacy_code = row['instance_legacy_code']
            court_district_legacy_code = row['court_district_legacy_code']
            person_court_legacy_code = row['person_court_legacy_code']
            court_division_legacy_code = row['court_division_legacy_code']
            law_suit_number = row['law_suit_number']

            lawsuit = self.model.objects.filter(legacy_code=legacy_code,
                                                system_prefix=LegacySystem.ADVWIN.value).first()
            folder = Folder.objects.filter(legacy_code=legacy_code).first()
            person_lawyer = Person.objects.filter(legacy_code=person_legacy_code).first()  # advogado burro
            instance = Instance.objects.filter(legacy_code=instance_legacy_code).first()
            court_district = CourtDistrict.objects.filter(name=court_district_legacy_code).first()  # court_district
            person_court = Person.objects.filter(legacy_code=person_court_legacy_code).first()  # campo donkey
            court_division = CourtDivision.objects.filter(legacy_code=court_division_legacy_code).first()

            if not folder:
                folder = Folder.objects.get(id=1)
            if not person_lawyer:
                person_lawyer = Person.objects.get(id=1)
            if not instance:
                instance = Instance.objects.get(id=1)
            if not court_district:
                court_district = CourtDistrict.objects.get(id=1)
            if not person_court:
                person_court = Person.objects.get(id=1)
            if not court_division:
                court_division = CourtDivision.objects.get(id=1)

            if lawsuit:
                lawsuit.folder = folder
                lawsuit.person_lawyer = person_lawyer
                lawsuit.instance = instance
                lawsuit.court_district = court_district
                lawsuit.court_division = court_division
                lawsuit.person_court = person_court
                lawsuit.law_suit_number = law_suit_number
                lawsuit.is_active = True
                # use update_fields to specify which fields to save
                # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                lawsuit.save(
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
                    instance=instance,
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
