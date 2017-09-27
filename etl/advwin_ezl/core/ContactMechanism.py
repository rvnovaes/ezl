from core.models import ContactMechanism, Person, ContactMechanismType
from django.db import IntegrityError
from etl.advwin_ezl.advwin_ezl import GenericETL


# noinspection SpellCheckingInspection
class ContactMechanismETL(GenericETL):
    model = ContactMechanism
    import_query = """
                    SELECT *
                    FROM (
                           --       ADV_PHONE1
                           SELECT
                             ADV_PHONE1.Codigo AS legacy_code,
                             'telefone'           AS contact_mechanism_type,
                             ADV_PHONE1.Fone1  AS description
                           FROM Jurid_Advogado AS ADV_PHONE1
                           WHERE ADV_PHONE1.Status = 'Ativo'
                                 AND ADV_PHONE1.Nome IS NOT NULL
                                 AND ADV_PHONE1.Nome <> ''
                                 AND ADV_PHONE1.Codigo NOT IN (SELECT CF.Codigo
                                                               FROM Jurid_CliFor AS CF
                                                               WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                           UNION
                    
                           --          ADV_PHONE2
                           SELECT
                             ADV_PHONE2.Codigo AS legacy_code,
                             'telefone'           AS contact_mechanism_type,
                             ADV_PHONE2.Fone2  AS description
                           FROM Jurid_Advogado AS ADV_PHONE2
                           WHERE ADV_PHONE2.Status = 'Ativo'
                                 AND ADV_PHONE2.Nome IS NOT NULL
                                 AND ADV_PHONE2.Nome <> ''
                                 AND ADV_PHONE2.Codigo NOT IN (SELECT CF.Codigo
                                                               FROM Jurid_CliFor AS CF
                                                               WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                    
                           UNION
                    
                           --   ADV_PHONE3
                           SELECT
                             ADV_PHONE3.Codigo AS legacy_code,
                             'telefone'           AS contact_mechanism_type,
                             ADV_PHONE3.FONE3  AS description
                           FROM Jurid_Advogado AS ADV_PHONE3
                           WHERE ADV_PHONE3.Status = 'Ativo'
                                 AND ADV_PHONE3.Nome IS NOT NULL
                                 AND ADV_PHONE3.Nome <> ''
                                 AND ADV_PHONE3.Codigo NOT IN (SELECT CF.Codigo
                                                               FROM Jurid_CliFor AS CF
                                                               WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                           UNION
                    
                           --   ADV_FAX
                           SELECT
                             ADV_FAX.Codigo AS legacy_code,
                             'telefone'        AS contact_mechanism_type,
                             ADV_FAX.Fax    AS description
                           FROM Jurid_Advogado AS ADV_FAX
                           WHERE ADV_FAX.Status = 'Ativo'
                                 AND ADV_FAX.Nome IS NOT NULL
                                 AND ADV_FAX.Nome <> ''
                                 AND ADV_FAX.Codigo NOT IN (SELECT CF.Codigo
                                                            FROM Jurid_CliFor AS CF
                                                            WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                    
                           --        ADV_EMAIL
                           UNION
                           SELECT
                             ADV_EMAIL.Codigo AS legacy_code,
                             'email'          AS contact_mechanism_type,
                             ADV_EMAIL.E_mail AS description
                           FROM Jurid_Advogado AS ADV_EMAIL
                           WHERE ADV_EMAIL.Status = 'Ativo'
                                 AND ADV_EMAIL.Nome IS NOT NULL
                                 AND ADV_EMAIL.Nome <> ''
                                 AND ADV_EMAIL.Codigo NOT IN (SELECT CF.Codigo
                                                              FROM Jurid_CliFor AS CF
                                                              WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                           UNION
                           --          CLIFOR_PHONE1
                           SELECT
                             CLIFOR_PHONE1.Codigo AS legacy_code,
                             'telefone'              AS contact_mechanism_type,
                             CLIFOR_PHONE1.Fone1  AS description
                           FROM Jurid_CliFor AS CLIFOR_PHONE1
                           WHERE CLIFOR_PHONE1.Status = 'Ativo' AND CLIFOR_PHONE1.Razao IS NOT NULL AND CLIFOR_PHONE1.Razao <> ''
                    
                           UNION
                           --          CLIFOR_PHONE2
                           SELECT
                             CLIFOR_PHONE2.Codigo AS legacy_code,
                             'telefone'              AS contact_mechanism_type,
                             CLIFOR_PHONE2.Fone2  AS description
                           FROM Jurid_CliFor AS CLIFOR_PHONE2
                           WHERE CLIFOR_PHONE2.Status = 'Ativo' AND CLIFOR_PHONE2.Razao IS NOT NULL AND CLIFOR_PHONE2.Razao <> ''
                    
                           UNION
                           --          CLIFOR_FAX
                           SELECT
                             CLIFOR_FAX.Codigo AS legacy_code,
                             'telefone'           AS contact_mechanism_type,
                             CLIFOR_FAX.Fax    AS description
                           FROM Jurid_CliFor AS CLIFOR_FAX
                           WHERE CLIFOR_FAX.Status = 'Ativo' AND CLIFOR_FAX.Razao IS NOT NULL AND CLIFOR_FAX.Razao <> ''
                    
                           UNION
                           --          CLIFOR_EMAIL
                           SELECT
                             CLIFOR_EMAIL.Codigo AS legacy_code,
                             'email'             AS contact_mechanism_type,
                             CLIFOR_EMAIL.E_mail AS description
                           FROM Jurid_CliFor AS CLIFOR_EMAIL
                           WHERE CLIFOR_EMAIL.Status = 'Ativo' AND CLIFOR_EMAIL.Razao IS NOT NULL AND CLIFOR_EMAIL.Razao <> ''
                    
                           UNION
                           --          CLIFOR_EMAILNFE
                           SELECT
                             CLIFOR_EMAILNFE.Codigo     AS legacy_code,
                             'email'                    AS contact_mechanism_type,
                             CLIFOR_EMAILNFE.email_nfse AS description
                           FROM Jurid_CliFor AS CLIFOR_EMAILNFE
                           WHERE CLIFOR_EMAILNFE.Status = 'Ativo' AND CLIFOR_EMAILNFE.Razao IS NOT NULL AND CLIFOR_EMAILNFE.Razao <> ''
                    
                           UNION
                           --          CLIFOR_SITE
                           SELECT
                             CLIFOR_SITE.Codigo AS legacy_code,
                             'email'            AS contact_mechanism_type,
                             CLIFOR_SITE.site   AS description
                           FROM Jurid_CliFor AS CLIFOR_SITE
                           WHERE CLIFOR_SITE.Status = 'Ativo' AND CLIFOR_SITE.Razao IS NOT NULL AND CLIFOR_SITE.Razao <> ''
                    
                           UNION
                           --          CORSER_EMAIL
                           SELECT
                             CORSER_EMAIL.CS_Advogado AS legacy_code,
                             'email'                  AS contact_mechanism_type,
                             CORSER_EMAIL.CS_Email    AS description
                           FROM Jurid_Corresp_Servico CORSER_EMAIL
                    
                           UNION
                           --          CORSER_MULTEMAIL
                           SELECT
                             CORSER_MULTEMAIL.CS_Advogado      AS legacy_code,
                             'muiltemail'                      AS contact_mechanism_type,
                             CORSER_MULTEMAIL.CS_Outros_Emails AS description
                           FROM Jurid_Corresp_Servico CORSER_MULTEMAIL
                    
                         ) AS TMP
                    WHERE description IS NOT NULL AND description <> ''
                    """
    has_status = True

    def config_import(self, rows, user, rows_count):
        #log_file = open('log_file.txt', 'w')
        for row in rows:
            print(rows_count)
            rows_count -= 1
            try:
                legacy_code = row['legacy_code']
                persons = Person.objects.filter(legacy_code=legacy_code)
                for person in persons:
                        description = ''
                        if row['contact_mechanism_type'] != 'muiltemail':
                            contact_mechanism_type = ContactMechanismType.objects.filter(
                                name__unaccent__iexact=row[
                                    'contact_mechanism_type']) or ContactMechanismType.objects.filter(
                                name__iexact='CONTACT MECHANISM TYPE-INVÁLIDO')
                            if contact_mechanism_type:
                                obj = self.model(contact_mechanism_type=contact_mechanism_type[0],
                                                 description=row['description'], notes='', person=person, create_user=user)
                                obj.save()
                        else:
                            contact_mechanism_type = ContactMechanismType.objects.filter(
                                name__unaccent__iexact='email') or ContactMechanismType.objects.filter(
                                name__iexact='MECANISMO-CONTATO-INVÁLIDO')
                            if contact_mechanism_type:
                                for description in row['description'].split(';'):
                                    if description:
                                        obj = self.model(contact_mechanism_type=contact_mechanism_type[0],
                                                         description=description, notes='', person=person, create_user=user)
                                        obj.save()

                        self.debug_logger.debug(
                            "Contact Mechanism,%s,%s,%s,%s,%s,%s" % (
                            str(legacy_code), str(contact_mechanism_type[0]), str(description), str(person.id),
                            str(user.id), self.timestr))
            except Exception as e:
                self.error_logger.error(
                    "Ocorreu o seguinte erro na importacao de ContactMechanism: " + str(rows_count) + "," + str(
                        e) + "," + self.timestr)

        super(ContactMechanismETL, self).config_import(rows, user, rows_count)


if __name__ == '__main__':
    ContactMechanismETL().import_data()
