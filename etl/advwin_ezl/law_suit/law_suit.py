# esse import deve vir antes de todos porque ele executa o __init__.py

from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from etl.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import LawSuit, Folder, Instance, CourtDistrict, CourtDivision


class LawsuitETL(GenericETL):
    model = LawSuit
    advwin_table = 'Jurid_Pastas'

    import_query = "SELECT top 1000" \
                   "   p.Codigo_Comp AS folder_legacy_code, " \
            "   case when (d.D_Atual is null) then 'False' else d.D_Atual end as is_current_instance, " \
            "   p.Advogado AS person_legacy_code, " \
            "   case when (rtrim(ltrim(d.D_Codigo)) LIKE '') or (d.D_Codigo is null) then " \
            "     p.Codigo_Comp else cast(d.D_Codigo as varchar(20)) end as legacy_code, " \
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
                   "    (d.D_Codigo_Inst IS NOT NULL AND d.D_Codigo_Inst <> '')) ORDER BY p.Dt_Cad DESC "

    has_status = True

    def config_import(self, rows, user, rows_count):
        for row in rows:
            print(rows_count)
            rows_count -= 1

            folder_legacy_code = row['folder_legacy_code']
            person_legacy_code = row['person_legacy_code']
            legacy_code = row['legacy_code']
            instance_legacy_code = row['instance_legacy_code']
            court_district_legacy_code = row['court_district_legacy_code']
            person_court_legacy_code = row['person_court_legacy_code']
            court_division_legacy_code = row['court_division_legacy_code']
            law_suit_number = row['law_suit_number']
            is_current_instance = row['is_current_instance']

            folder = Folder.objects.filter(legacy_code=folder_legacy_code).first()
            person_lawyer = Person.objects.filter(legacy_code=person_legacy_code).first()
            instance = Instance.objects.filter(legacy_code=instance_legacy_code).first()
            # __iexact - Case-insensitive exact match.
            # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#std:fieldlookup-iexact
            court_district = CourtDistrict.objects.filter(name__unaccent__iexact=court_district_legacy_code).first()
            person_court = Person.objects.filter(legacy_code=person_court_legacy_code).first()
            court_division = CourtDivision.objects.filter(legacy_code=court_division_legacy_code).first()

            # se não encontrou o registro, busca o registro inválido
            if not folder:
                folder = InvalidObjectFactory.get_invalid_model(Folder)
            if not person_lawyer:
                person_lawyer = InvalidObjectFactory.get_invalid_model(Person)
            if not instance:
                instance = InvalidObjectFactory.get_invalid_model(Instance)
            if not court_district:
                court_district = InvalidObjectFactory.get_invalid_model(CourtDistrict)
            if not person_court:
                person_court = InvalidObjectFactory.get_invalid_model(Person)
            if not court_division:
                court_division = InvalidObjectFactory.get_invalid_model(CourtDivision)

            lawsuit = self.model.objects.filter(instance=instance,
                                                law_suit_number=law_suit_number).first()

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
                        'alter_date',
                        'is_current_instance']
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
                    is_current_instance=is_current_instance,
                    legacy_code=legacy_code,
                    system_prefix=LegacySystem.ADVWIN.value)

            super(LawsuitETL, self).config_import(rows, user, rows_count)


if __name__ == "__main__":
    LawsuitETL().import_data()
