from core.models import ContactMechanism, Person, ContactMechanismType
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import get_message_log_default, save_error_log


# noinspection SpellCheckingInspection
class ContactMechanismETL(GenericETL):
    model = ContactMechanism
    import_query = """
                
        SELECT *
                    FROM (
                           --       ADV_PHONE1
                           SELECT
                             ADV_PHONE1.Codigo AS legacy_code,
                             'telefone'        AS contact_mechanism_type,
                             ADV_PHONE1.Fone1  AS description
                           FROM Jurid_Advogado AS ADV_PHONE1
                           WHERE ADV_PHONE1.Status = 'Ativo'
                               AND Unidade IN ('21', '11', '14', '24', '09', '06', '13', '01')
                               AND ADV_PHONE1.Fone1 IS NOT NULL
                                 AND ADV_PHONE1.Nome IS NOT NULL
                                 AND ADV_PHONE1.Nome <> ''
                                 AND ADV_PHONE1.Codigo NOT IN (
                             SELECT CF.Codigo
                             FROM Jurid_CliFor AS CF
                             WHERE CF.Status = 'Ativo'
                                   AND CF.Razao IS NOT NULL
                                   AND CF.Razao <> ''
                                   AND CF.Fone1 IS NOT NULL
                           )
                           UNION
                           --          ADV_PHONE2
                           SELECT
                             ADV_PHONE2.Codigo AS legacy_code,
                             'telefone'        AS contact_mechanism_type,
                             ADV_PHONE2.Fone2  AS description
                           FROM Jurid_Advogado AS ADV_PHONE2
                           WHERE ADV_PHONE2.Status = 'Ativo'
                               AND Unidade IN ('21', '11', '14', '24', '09', '06', '13', '01')
                               AND ADV_PHONE2.Fone2 IS NOT NULL                           
                                 AND ADV_PHONE2.Nome IS NOT NULL
                                 AND ADV_PHONE2.Nome <> ''
                                 AND ADV_PHONE2.Codigo NOT IN (
                             SELECT CF.Codigo
                             FROM Jurid_CliFor AS CF
                             WHERE CF.Status = 'Ativo'
                                   AND CF.Razao IS NOT NULL
                                   AND CF.Razao <> ''
                                   AND CF.Fone2 IS NOT NULL
                           )
                           UNION
                           --   ADV_PHONE3
                           SELECT
                             ADV_PHONE3.Codigo AS legacy_code,
                             'telefone'        AS contact_mechanism_type,
                             ADV_PHONE3.FONE3  AS description
                           FROM Jurid_Advogado AS ADV_PHONE3
                           WHERE ADV_PHONE3.Status = 'Ativo'
                               AND Unidade IN ('21', '11', '14', '24', '09', '06', '13', '01')
                               AND ADV_PHONE3.Fone3 IS NOT NULL                           
                                 AND ADV_PHONE3.Nome IS NOT NULL
                                 AND ADV_PHONE3.Nome <> ''
                                 AND ADV_PHONE3.Codigo NOT IN (
                             SELECT CF.Codigo
                             FROM Jurid_CliFor AS CF
                             WHERE CF.Status = 'Ativo'
                                   AND CF.Razao IS NOT NULL
                                   AND CF.Razao <> ''
                           )
                           --        ADV_EMAIL
                           UNION
                           SELECT DISTINCT
                             ADV_EMAIL.Codigo AS legacy_code,
                             'email'          AS contact_mechanism_type,
                             ADV_EMAIL.E_mail AS description
                           FROM Jurid_Advogado AS ADV_EMAIL
                           WHERE ADV_EMAIL.Status = 'Ativo'
                                 AND LOWER(ADV_EMAIL.E_mail) like '%@mtostes.com.br' 
                                 AND ADV_EMAIL.Nome IS NOT NULL
                                 AND ADV_EMAIL.Nome <> ''
                                 AND ADV_EMAIL.Codigo NOT IN (
                             SELECT CF.Codigo
                             FROM Jurid_CliFor AS CF
                             WHERE CF.Status = 'Ativo'
                                   AND CF.Razao IS NOT NULL
                                   AND CF.Razao <> ''
                                   AND CF.E_mail IS NOT NULL
                           )
                    
                           UNION
                           --          CORSER_EMAIL
                           SELECT DISTINCT
                             CORSER_EMAIL.CS_Advogado AS legacy_code,
                             'email'                  AS contact_mechanism_type,
                             CORSER_EMAIL.CS_Email    AS description
                           FROM Jurid_Corresp_Servico CORSER_EMAIL
                           WHERE LOWER(CORSER_EMAIL.CS_Email) LIKE '%@mtostes.com.br'  
                    
                           UNION
                           --          CORSER_MULTEMAIL
                           SELECT DISTINCT
                             CORSER_MULTEMAIL.CS_Advogado      AS legacy_code,
                             'multemail'                       AS contact_mechanism_type,
                             CORSER_MULTEMAIL.CS_Outros_Emails AS description
                           FROM Jurid_Corresp_Servico CORSER_MULTEMAIL
                           WHERE LOWER(CORSER_MULTEMAIL.CS_Outros_Emails) LIKE '%@mtostes.com.br%' -- Necessario tratar no codigo pois vem mais de um email no campo
                         ) AS TMP
                    WHERE description IS NOT NULL AND description <> ''
                    """
    has_status = False    
    field_check = 'description'

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                persons = Person.objects.filter(legacy_code=legacy_code)
                for person in persons:
                        description = ''
                        if row['contact_mechanism_type'] != 'multemail':
                            contact_mechanism_type, created = ContactMechanismType.objects.get_or_create(
                                defaults={'name': row['contact_mechanism_type'],
                                          'create_user': user},
                                name__unaccent__iexact=row['contact_mechanism_type'])
                            if contact_mechanism_type:
                                obj = self.model(contact_mechanism_type=contact_mechanism_type,
                                                 description=row['description'], notes='', person=person,
                                                 create_user=user)
                                obj.save()
                        else:
                            contact_mechanism_type, created = ContactMechanismType.objects.get_or_create(
                                defaults={'name': 'email',
                                            'create_user': user},
                                name__unaccent__iexact = 'email')
                            if contact_mechanism_type:
                                for description in row['description'].split(';'):
                                    if '@mtostes.com.br' in description.lower():
                                        obj = self.model(contact_mechanism_type=contact_mechanism_type,
                                                         description=description, notes='', person=person,
                                                         create_user=user)
                                        obj.save()

                        self.debug_logger.debug(
                            "Contact Mechanism,%s,%s,%s,%s,%s,%s" % (
                            str(legacy_code), str(contact_mechanism_type), str(description), str(person.id),
                            str(user.id), self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                save_error_log(log, user, msg)


if __name__ == '__main__':
    ContactMechanismETL().import_data()
