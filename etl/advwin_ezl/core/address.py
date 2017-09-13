from core.models import Address, Person, AddressType, City, State, Country
from django.db import IntegrityError
from etl.advwin_ezl.advwin_ezl import GenericETL


# noinspection SpellCheckingInspection
class AddressETL(GenericETL):
    model = Address
    import_query = """
                SELECT
                  codigo      AS legacy_code,
                  endereco    AS street,
                  cidade      AS city,
                  bairro      AS city_region,
                  cep         AS zip_code,
                  uf          AS state,
                  numero_end  AS number,
                  complemento AS complement,
                  pais        AS country,
                  'comercial'      AS address_type
                FROM jurid_advogado AS ADV_END
                WHERE ADV_END.Status = 'Ativo'
                      AND ADV_END.Nome IS NOT NULL
                      AND ADV_END.Nome <> ''
                      AND ADV_END.Codigo NOT IN (SELECT CF.Codigo
                                                 FROM Jurid_CliFor AS CF
                                                 WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                UNION
                SELECT
                  codigo      AS legacy_code,
                  endereco    AS street,
                  cidade      AS city,
                  bairro      AS city_region,
                  cep         AS zip_code,
                  uf          AS state,
                  Numero      AS number,
                  complemento AS complement,
                  pais        AS country,
                  'comercial'      AS address_type
                FROM Jurid_CliFor AS CLIFOR_END
                WHERE CLIFOR_END.Status = 'Ativo' AND CLIFOR_END.Razao IS NOT NULL AND CLIFOR_END.Razao <> ''
                UNION
                SELECT
                  codigo          AS legacy_code,
                  Cob_endereco    AS street,
                  Cob_Cidade      AS city,
                  Cob_Bairro      AS city_region,
                  Cob_CEP         AS zip_code,
                  Cob_UF          AS state,
                  Cob_Numero      AS number,
                  Cob_Complemento AS complement,
                  Cob_pais        AS country,
                  'cobranca'      AS address_type
                FROM Jurid_CliFor AS CLIFOR_END_COB
                WHERE CLIFOR_END_COB.Status = 'Ativo' AND CLIFOR_END_COB.Razao IS NOT NULL AND CLIFOR_END_COB.Razao <> ''
                    """
    has_status = True

    def config_import(self, rows, user, rows_count):
        log_file = open('log_file.txt', 'w')
        for row in rows:
            print(rows_count)
            rows_count -= 1
            legacy_code = row['legacy_code']
            persons = Person.objects.filter(legacy_code=legacy_code)
            address_type = AddressType.objects.filter(name__iexact=row['address_type'])
            if not address_type:
                AddressType.objects.create(name=row['address_type'], create_user=user)
                address_type = AddressType.objects.filter(name__iexact=row['address_type'])
            address_type = address_type[0]
            for person in persons:
                country = Country.objects.filter(
                    name__unaccent__iexact=row['country'].strip() if row['country'] else '') or Country.objects.filter(
                    name__unaccent__iexact='PAÍS-INVÁLIDO')
                state = State.objects.filter(
                    initials__iexact=row['state'].strip() if row['state'] else '') or State.objects.filter(
                    name__iexact='ESTADO-INVÁLIDO')
                city = City.objects.filter(name__unaccent__iexact=row['city'].strip() if row['city'] else '',
                                           state=state) or City.objects.filter(
                    name__unaccent__iexact='CIDADE-INVÁLIDO')
                obj = self.model(person=person,
                                 street=row['street'] or '',
                                 number=row['number'] or '',
                                 complement=row['complement'] or '',
                                 city_region=row['city_region'] or '',
                                 zip_code=row['zip_code'] or '',
                                 address_type=address_type,
                                 state=state[0],
                                 city=city[0],
                                 country=country[0],
                                 alter_user=user,
                                 create_user=user)
                try:
                    obj.save()
                except IntegrityError:
                    log_file.write(str(row) + '')
        super(AddressETL, self).config_import(rows, user, rows_count)


if __name__ == '__main__':
    AddressETL().import_data()
