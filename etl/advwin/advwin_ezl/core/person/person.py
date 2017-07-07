# esse import deve vir antes de todos porque ele executa o __init__.py
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL

from django.db import IntegrityError

from core.models import Person
from core.utils import LegacySystem


class PersonETL(GenericETL):
    advwin_table = ['Jurid_Clifor', 'Jurid_Advogado', 'Jurid_Tribunais']
    model = Person

    query = "select \n" \
            "  cf1.Razao as legal_name, \n" \
            "  cf1.Nome as name, \n" \
            "  cf1.Codigo as legacy_code, \n" \
            "  CASE cf1.pessoa_fisica WHEN 0 THEN 'J' ELSE 'F' END as legal_type, \n" \
            "  cf1.TipoCF as customer_supplier, \n" \
            "  'False' AS is_lawyer, \n" \
            "  'False' AS is_correspondent, \n" \
            "  'False' AS is_court \n" \
            "from " + advwin_table[0] + " as cf1 \n" \
            "where \n" \
            "  cf1.Status = 'Ativo' and \n" \
            "  cf1.Razao is not null and cf1.Razao <> '' and \n" \
            "  cf1.Codigo = ( \n" \
            "    select min(cf2.Codigo) \n" \
            "    from Jurid_CliFor as cf2 \n" \
            "    where \n" \
            "      cf2.Status = 'Ativo' and \n" \
            "      cf2.Razao is not null and cf2.Razao <> '' and \n" \
            "      cf1.Codigo = cf2.Codigo) \n" \
            " \n" \
            "UNION \n" \
            " \n" \
            "select \n" \
            "  a1.Nome as legal_name, \n" \
            "  a1.Nome as name, \n" \
            "  a1.Codigo as legacy_code, \n" \
            "  'N/D' as legal_type, \n" \
            "  'F' as customer_supplier, \n" \
            "  'True' AS is_lawyer, \n" \
            "  CASE a1.Correspondente WHEN 0 THEN 'False' ELSE 'True' END as is_correspondent, \n" \
            "  'False' AS is_court \n" \
            "from " + advwin_table[1] + " as a1 \n" \
            "where \n" \
            "  a1.Status = 'Ativo' and \n" \
            "  a1.Nome is not null and a1.Nome <> '' and \n" \
            "  a1.Codigo = ( \n" \
            "  select min(a2.Codigo) \n" \
            "  from Jurid_Advogado as a2 \n" \
            "  where \n" \
            "    a2.Status = 'Ativo' and \n" \
            "    a2.Nome is not null and a2.Nome <> '' and \n" \
            "    a1.Codigo = a2.Codigo) \n" \
            " \n" \
            "UNION \n" \
            " \n" \
            "select \n" \
            "  t1.Descricao as legal_name, \n" \
            "  t1.Descricao as name, \n" \
            "  t1.Codigo as legacy_code, \n" \
            "  'J' as legal_type, \n" \
            "  'F' as customer_supplier, \n" \
            "  'False' AS is_lawyer, \n" \
            "  'False' AS is_correspondent, \n" \
            "  'True' AS is_court \n" \
            "from " + advwin_table[2] + " as t1 \n" \
            "where \n" \
            "  t1.Descricao is not null and t1.Descricao <> '' and \n" \
            "  t1.Codigo = ( \n" \
            "  select min(t2.Codigo) \n" \
            "  from Jurid_Tribunais as t2 \n" \
            "  where \n" \
            "    t2.Descricao is not null and t2.Descricao <> '' and \n" \
            "    t1.Codigo = t2.Codigo)"
    has_status = True

    def load_etl(self, rows, user):
        log_file = open('log_file.txt', 'w')
        for row in rows:
            print(row)

            legal_name = row['legal_name']
            name = row['name']
            legacy_code = row['legacy_code']
            legal_type = row['legal_type']
            customer_supplier = row['customer_supplier']
            is_lawyer = row['is_lawyer']
            is_correspondent = row['is_correspondent']
            is_court = row['is_court']

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
                is_client = True
                is_provider = True
            elif customer_supplier == 'C':
                is_client = True
                is_provider = False
            elif customer_supplier == 'F':
                is_client = False
                is_provider = True
            else:
                is_client = False
                is_provider = False

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
                instance.is_client = is_client
                instance.is_provider = is_provider
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
                                   'is_client',
                                   'is_provider'])
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
                                 is_client=is_client,
                                 is_provider=is_provider,
                                 legacy_code=legacy_code,
                                 system_prefix=LegacySystem.ADVWIN.value)
                try:
                    obj.save()
                except IntegrityError:
                    log_file.write(str(row) + '\n')

            super(PersonETL, self).load_etl(rows, user)


if __name__ == "__main__":
    PersonETL().import_data()
