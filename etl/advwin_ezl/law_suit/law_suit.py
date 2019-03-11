from core.models import Person, State, City
from core.utils import LegacySystem
from lawsuit.models import Organ, CourtDistrictComplement, TypeLawsuit
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory, INVALID_ORGAN
from etl.utils import get_clients_to_import
from lawsuit.models import LawSuit, Folder, Instance, CourtDistrict, CourtDivision
from etl.utils import get_message_log_default, save_error_log
import json


class LawsuitETL(GenericETL):
    model = LawSuit
    advwin_table = 'Jurid_Pastas'

    _import_query = """
                    SELECT
                          p.OutraParte                             AS opposing_party,
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
                          d.D_UF                                   AS state_court_district_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Tribunal)) LIKE '') OR (d.D_Tribunal IS NULL)
                            THEN
                              p.Tribunal
                          ELSE d.D_Tribunal END                    AS person_court_legacy_code,
                          CASE WHEN (rtrim(ltrim(d.D_Vara)) LIKE '') OR (d.D_Vara IS NULL)
                            THEN
                              p.Varas
                          ELSE d.D_Vara END                        AS court_division_legacy_code,
                          d.D_NumPrc                               AS law_suit_number
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
                          (p.Status = 'Ativa' OR p.Status = 'Especial') AND
                          cm.UsarOS = 1 AND
                          p.Cliente IS NOT NULL AND p.Cliente <> '' AND
                          (a.SubStatus = 10 OR a.SubStatus = 11) AND
                          a.Status = '0' AND -- STATUS ATIVO
                          p.Cliente IN ('{cliente}')
                          AND
                          ((p.Codigo_Comp IS NOT NULL AND p.Codigo_Comp <> '') OR
                           (d.Codigo_Comp IS NOT NULL AND d.Codigo_Comp <> '')) AND
                          ((p.Instancia IS NOT NULL AND p.Instancia <> '') OR
                           (d.D_Codigo_Inst IS NOT NULL AND d.D_Codigo_Inst <> ''))

    """

    has_status = True

    @property
    def import_query(self):
        return self._import_query.format(
            cliente="','".join(get_clients_to_import(self.default_office)))

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        import pdb;pdb.set_trace()
        insert_records = []
        for row in rows:
            rows_count -= 1

            try:
                folder_legacy_code = row['folder_legacy_code']
                person_legacy_code = row['person_legacy_code']
                legacy_code = row['legacy_code']
                instance_legacy_code = row['instance_legacy_code']
                court_district_legacy_code = row['court_district_legacy_code']
                state_court_district_legacy_code = row[
                    'state_court_district_legacy_code']
                person_court_legacy_code = row['person_court_legacy_code']
                court_division_legacy_code = row['court_division_legacy_code']
                law_suit_number = row['law_suit_number']
                is_current_instance = row['is_current_instance']
                opposing_party = row['opposing_party']
                folder = Folder.objects.filter(
                    legacy_code=folder_legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                person_lawyer = Person.objects.filter(
                    legacy_code=person_legacy_code,
                    legacy_code__isnull=False,
                    offices=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                instance = Instance.objects.filter(
                    legacy_code=instance_legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                state = State.objects.filter(
                    initials=state_court_district_legacy_code).first()

                # __iexact - Case-insensitive exact match.
                # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#std:fieldlookup-iexact
                # 1. tenta localizar como comarca no EZL. Se achar, salva a comarca.
                # 2. tenta localizar como cidade no EZL. Se achar, salva a cidade e a comarca
                # 3. tenta localizar como Complemento no EZL. Se achar, salva o complemento e a comarca.
                court_district = CourtDistrict.objects.filter(
                    name__unaccent__iexact=court_district_legacy_code,
                    state=state, is_active=True).first()
                city = City.objects.filter(
                    name__unaccent__iexact=court_district_legacy_code,
                    state=state, is_active=True).first()
                court_district_complement = CourtDistrictComplement.objects.filter(
                    name__unaccent__iexact=court_district_legacy_code,
                    court_district__state=state, is_active=True).first()

                organ = Organ.objects.filter(
                    legacy_code=person_court_legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                court_division = CourtDivision.objects.filter(
                    legacy_code=court_division_legacy_code,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()

                # se não encontrou o registro, busca o registro inválido
                if not folder:
                    folder = InvalidObjectFactory.get_invalid_model(Folder)
                if not person_lawyer:
                    person_lawyer = InvalidObjectFactory.get_invalid_model(
                        Person)
                if not instance:
                    instance = InvalidObjectFactory.get_invalid_model(Instance)

                # se a instancia for administrativa o tipo do processo tambem sera
                if str(instance_legacy_code) == '1' or str(instance_legacy_code) == '5':
                    type_lawsuit = TypeLawsuit.ADMINISTRATIVE.name
                else:
                    type_lawsuit = TypeLawsuit.JUDICIAL.name

                # se não encontrou o complemento, a cidade e a comarca, coloca OS no status de Erro
                if court_district is None and city is None and court_district_complement is None and \
                        court_district_legacy_code:
                    court_district = InvalidObjectFactory.get_invalid_model(
                        CourtDistrict)
                else:
                    # se não encontrou a comarca e encontrou a cidade, busca a comarca salva na cidade
                    if city and not court_district:
                        court_district = city.court_district
                    # se não encontrou a cidade, busca a cidade salva no complemento da comarca
                    if court_district_complement and not court_district and not city:
                        court_district = court_district_complement.court_district

                if not organ:
                    organ = Organ.objects.filter(
                        legal_name=INVALID_ORGAN).first()
                if not court_division:
                    court_division = InvalidObjectFactory.get_invalid_model(
                        CourtDivision)

                lawsuit = self.model.objects.filter(
                    legacy_code=legacy_code,
                    legacy_code__isnull=False,
                    office=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()

                if lawsuit:
                    lawsuit.legacy_code = legacy_code
                    lawsuit.folder = folder
                    lawsuit.person_lawyer = person_lawyer
                    lawsuit.instance = instance
                    lawsuit.court_district = court_district
                    lawsuit.court_division = court_division
                    lawsuit.organ = organ
                    if law_suit_number:
                        lawsuit.law_suit_number = law_suit_number
                    lawsuit.is_active = True
                    lawsuit.opposing_party = opposing_party
                    lawsuit.office = default_office
                    lawsuit.alter_user = user
                    lawsuit.city = city
                    lawsuit.court_district_complement = court_district_complement
                    lawsuit.type_lawsuit = type_lawsuit
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    lawsuit.save(update_fields=[
                        'legacy_code', 'is_active', 'folder', 'person_lawyer', 'instance', 'court_district',
                        'court_division', 'organ', 'law_suit_number', 'alter_user', 'alter_date','is_current_instance',
                        'opposing_party', 'office', 'city', 'court_district_complement', 'type_lawsuit'
                    ])
                else:
                    insert_records.append(json.dumps({
                        'folder_id': folder.id if folder else None,
                        'person_lawyer_id': person_lawyer.id if person_lawyer else None,
                        'instance_id': instance.id if instance else None,
                        'court_district_id': court_district.id if court_district else None,
                        'court_division_id': court_division.id if court_division else None,
                        'organ_id': organ.id if organ else None,
                        'law_suit_number': law_suit_number,
                        'alter_user_id': user.id,
                        'create_user_id': user.id,
                        'is_active': True,
                        'is_current_instance': is_current_instance,
                        'legacy_code': legacy_code,
                        'system_prefix': LegacySystem.ADVWIN.value,
                        'opposing_party': opposing_party,
                        'office_id': default_office.id,
                        'city_id': city.id if city else None,
                        'court_district_complement': court_district_complement.id if court_district_complement else None,
                        'type_lawsuit': type_lawsuit}, sort_keys=True))
                self.debug_logger.debug(
                    "LawSuit,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
                    % (str(folder.id), str(person_lawyer.id), str(instance.id),
                       str(court_district.id if court_district else 0), str(court_division.id),
                       str(organ.id), law_suit_number, str(user.id),
                       str(user.id), str(True), str(is_current_instance),
                       legacy_code, str(LegacySystem.ADVWIN.value),
                       str(opposing_party), self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)
        if insert_records:

            self.model.objects.bulk_create([
                self.model(**json.loads(item)) for item in set(insert_records)
            ], batch_size=1000)


if __name__ == "__main__":
    LawsuitETL().import_data()
