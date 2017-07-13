# esse import deve vir antes de todos porque ele executa o __init__.py
from django.db import IntegrityError

from core.models import Person
from core.utils import LegacySystem
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL


class PersonETL(GenericETL):
    advwin_table = ['Jurid_Tribunais', 'Jurid_Advogado', 'Jurid_Clifor']
    model = Person

    query = "select" \
            "  t1.Descricao as legal_name, " \
            "  t1.Descricao as name, " \
            "  t1.Codigo as legacy_code, " \
            "  'J' as legal_type, " \
            "  'F' as customer_supplier, " \
            "  'False' AS is_lawyer, " \
            "  'False' AS is_correspondent, " \
            "  'True' AS is_court " \
            "from " + advwin_table[0] + " as t1 " \
                                        "where " \
                                        "  t1.Descricao is not null and t1.Descricao <> '' and " \
                                        "  t1.Codigo = ( " \
                                        "  select min(t2.Codigo) " \
                                        "  from " + advwin_table[0] + " as t2 " \
                                                                      "  where " \
                                                                      "    t2.Descricao is not null and t2.Descricao <> '' and " \
                                                                      "    t1.Codigo = t2.Codigo) " \
                                                                      " " \
                                                                      "UNION " \
                                                                      " " \
                                                                      "select " \
                                                                      "  a1.Nome as legal_name, " \
                                                                      "  a1.Nome as name, " \
                                                                      "  a1.Codigo as legacy_code, " \
                                                                      "  'N/D' as legal_type, " \
                                                                      "  'F' as customer_supplier, " \
                                                                      "  'True' AS is_lawyer, " \
                                                                      "  CASE a1.Correspondente WHEN 0 THEN 'False' ELSE 'True' END as is_correspondent, " \
                                                                      "  'False' AS is_court " \
                                                                      "from " + advwin_table[1] + " as a1 " \
                                                                                                  "where " \
                                                                                                  "  a1.Status = 'Ativo' and " \
                                                                                                  "  a1.Nome is not null and a1.Nome <> '' and " \
                                                                                                  "  a1.Codigo not in ( " \
                                                                                                  "  select cf.Codigo " \
                                                                                                  "  from " + \
            advwin_table[2] + " as cf " \
                              "  where " \
                              "      cf.Status = 'Ativo' and " \
                              "      cf.Razao is not null and cf.Razao <> '') " \
                              " " \
                              "UNION " \
                              " " \
                              "select " \
                              "  cf.Razao as legal_name, " \
                              "  cf.Nome as name, " \
                              "  cf.Codigo as legacy_code, " \
                              "  CASE cf.pessoa_fisica WHEN 0 THEN 'J' ELSE 'F' END as legal_type, " \
                              "  cf.TipoCF as customer_supplier, " \
                              "  'False' AS is_lawyer, " \
                              "  'False' AS is_correspondent, " \
                              "  'False' AS is_court " \
                              "from " + advwin_table[2] + " as cf " \
                                                          "where " \
                                                          "  cf.Status = 'Ativo' and " \
                                                          "  cf.Razao is not null and cf.Razao <> ''"

    has_status = True

    def load_etl(self, rows, user):
        log_file = open('log_file.txt', 'w')
        for row in rows:
            print(row)

            legal_name = row['legal_name'] or row['name']
            name = row['name'] or row['legal_name']
            legacy_code = row['legacy_code']
            legal_type = row['legal_type']
            customer_supplier = row['customer_supplier']
            is_lawyer = row['is_lawyer']
            is_correspondent = row['is_correspondent']
            is_court = row['is_court']
            cpf_cnpj = None
            if legal_type != 'F' and legal_type != 'J':
                if str(legacy_code).isnumeric():
                    # se for maior que 11 provavelmente é o cnpj
                    if len(legacy_code) > 11:
                        legal_type = 'J'
                    else:
                        legal_type = 'F'
                else:
                    # se nao der pra saber se é pessoa fisica ou juridica será considerada juridica
                    legal_type = 'J'

            if str(legacy_code).isnumeric():
                # no advwin nao tem campo para cpf_cnpj, é salvo no codigo
                cpf_cnpj = legacy_code

            if customer_supplier == 'A':
                is_customer = True
                is_supplier = True
            elif customer_supplier == 'C':
                is_customer = True
                is_supplier = False
            elif customer_supplier == 'F':
                is_customer = False
                is_supplier = True
            else:
                is_customer = False
                is_supplier = False

            is_active = True

            instance = self.model.objects.filter(legacy_code=legacy_code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()

            if instance:
                # use update_fields to specify which fields to save
                # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                instance.legal_name = legal_name
                instance.name = name
                instance.is_lawyer = is_lawyer
                instance.is_correspondent = is_correspondent
                instance.is_court = is_court
                instance.legal_type = legal_type
                instance.cpf_cnpj = cpf_cnpj
                instance.alter_user = user
                instance.is_customer = is_customer
                instance.is_supplier = is_supplier
                instance.is_active = is_active
                instance.save(
                    update_fields=['alter_date',
                                   'legal_name',
                                   'name',
                                   'is_lawyer',
                                   'is_correspondent',
                                   'is_court',
                                   'legal_type',
                                   'cpf_cnpj',
                                   'alter_user',
                                   'is_active',
                                   'is_customer',
                                   'is_supplier'])
            else:
                obj = self.model(legal_name=legal_name,
                                 name=name,
                                 is_lawyer=is_lawyer,
                                 is_correspondent=is_correspondent,
                                 is_court=is_court,
                                 legal_type=legal_type,
                                 cpf_cnpj=cpf_cnpj,
                                 alter_user=user,
                                 create_user=user,
                                 is_customer=is_customer,
                                 is_supplier=is_supplier,
                                 is_active=is_active,
                                 legacy_code=legacy_code,
                                 system_prefix=LegacySystem.ADVWIN.value)
                try:
                    obj.save()
                except IntegrityError:
                    log_file.write(str(row) + '')

            super(PersonETL, self).load_etl(rows, user)


if __name__ == "__main__":
    PersonETL().import_data()
