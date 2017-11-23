from core.models import Person
from core.utils import LegacySystem
from lawsuit.models import Organ
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from lawsuit.models import LawSuit, Folder, Instance, CourtDistrict, CourtDivision
from etl.utils import get_message_log_default, save_error_log


class LawsuitETL(GenericETL):
    model = LawSuit
    advwin_table = 'Jurid_Pastas'

    import_query = """
                    SELECT DISTINCT
                          p.Codigo_Comp                            AS folder_legacy_code,
                          CASE WHEN (d.D_Atual IS NULL)
                            THEN 'False'
                          ELSE d.D_Atual END                       AS is_current_instance,
                          p.Advogado                               AS person_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Codigo)) LIKE '') OR (d.D_Codigo IS NULL)
                            THEN
                              p.Codigo_Comp
                          ELSE cast(d.D_Codigo AS VARCHAR(20)) END AS legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Codigo_Inst)) LIKE '') OR (d.D_Codigo_Inst IS NULL)
                            THEN
                              p.Instancia
                          ELSE d.D_Codigo_Inst END                 AS instance_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Comarca)) LIKE '') OR (d.D_Comarca IS NULL)
                            THEN
                              p.Comarca
                          ELSE d.D_Comarca END                     AS court_district_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Tribunal)) LIKE '') OR (d.D_Tribunal IS NULL)
                            THEN
                              p.Tribunal
                          ELSE d.D_Tribunal END                    AS person_court_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Vara)) LIKE '') OR (d.D_Vara IS NULL)
                            THEN
                              p.Varas
                          ELSE d.D_Vara END                        AS court_division_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_NumPrc)) LIKE '') OR (d.D_NumPrc IS NULL)
                            THEN
                              p.NumPrc1
                          ELSE d.D_NumPrc END                      AS law_suit_number
                    FROM Jurid_Pastas AS p
                          LEFT JOIN Jurid_Distribuicao AS d ON
                                                              p.Codigo_Comp = d.Codigo_Comp
                          INNER JOIN Jurid_ProcMov AS pm ON
                                                           pm.Codigo_Comp = p.Codigo_Comp
                          INNER JOIN Jurid_agenda_table AS a ON
                                                               pm.Ident = a.Mov
                          INNER JOIN Jurid_CodMov AS cm ON
                                                          a.CodMov = cm.Codigo
                    WHERE
                          p.Status = 'Ativa' AND
                          p.Dt_Saida IS NULL AND
                          cm.UsarOS = 1 AND
                          p.Cliente IS NOT NULL AND p.Cliente <> '' AND
                          ((a.prazo_lido = 0 AND a.SubStatus = 30) OR
                          (a.SubStatus = 80)) AND a.Status = '0' -- STATUS ATIVO
                          AND a.Advogado IN ('12157458697', '12197627686', '13281750656') AND -- marcio.batista, nagila e claudia (Em teste)
                          ((p.NumPrc1 IS NOT NULL AND p.NumPrc1 <> '') OR
                           (d.D_NumPrc IS NOT NULL AND d.D_NumPrc <> '')) AND
                          ((p.Codigo_Comp IS NOT NULL AND p.Codigo_Comp <> '') OR
                           (d.Codigo_Comp IS NOT NULL AND d.Codigo_Comp <> '')) AND
                          ((p.Instancia IS NOT NULL AND p.Instancia <> '') OR
                           (d.D_Codigo_Inst IS NOT NULL AND d.D_Codigo_Inst <> ''))

    """

    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        for row in rows:
            print(rows_count)
            rows_count -= 1

            try:
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
                organ = Organ.objects.filter(legacy_code=person_court_legacy_code).first()
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
                if not organ:
                    organ = InvalidObjectFactory.get_invalid_model(Person)
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
                    lawsuit.organ = organ
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
                            'organ',
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
                        organ=organ,
                        law_suit_number=law_suit_number,
                        alter_user=user,
                        create_user=user,
                        is_active=True,
                        is_current_instance=is_current_instance,
                        legacy_code=legacy_code,
                        system_prefix=LegacySystem.ADVWIN.value)

                self.debug_logger.debug(
                    "LawSuit,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (str(folder.id), str(person_lawyer.id),
                                                                           str(instance.id),str(court_district.id),
                                                      str(court_division.id), str(organ.id),law_suit_number,
                                                      str(user.id),str(user.id),str(True),str(is_current_instance),
                                                      legacy_code,str(LegacySystem.ADVWIN.value), self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)

if __name__ == "__main__":
    LawsuitETL().import_data()
