from core.models import Address, Person, AddressType, City, State, Country
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import get_message_log_default, save_error_log
from core.utils import LegacySystem


# noinspection SpellCheckingInspection
class AddressETL(GenericETL):
    model = Address
    field_check = 'person__legacy_code'
    import_query = """
                    SELECT
                      codigo      AS person__legacy_code,
                      endereco    AS street,
                      cidade      AS city,
                      bairro      AS city_region,
                      cep         AS zip_code,
                      uf          AS state,
                      numero_end  AS number,
                      complemento AS complement,
                      pais        AS country,
                      'comercial' AS address_type
                    FROM jurid_advogado AS ADV_END
                    WHERE ADV_END.Status = 'Ativo'
                          AND ADV_END.Nome IS NOT NULL
                          AND ADV_END.Nome <> ''
                          AND ADV_END.Codigo NOT IN (SELECT CF.Codigo
                                                     FROM Jurid_CliFor AS CF
                                                     WHERE CF.Status = 'Ativo' AND CF.Razao IS NOT NULL AND CF.Razao <> '')
                          AND (endereco IS NOT NULL OR cidade IS NOT NULL OR bairro IS NOT NULL OR uf IS NOT NULL)
                    UNION
                    SELECT
                      codigo      AS person__legacy_code,
                      endereco    AS street,
                      cidade      AS city,
                      bairro      AS city_region,
                      cep         AS zip_code,
                      uf          AS state,
                      Numero      AS number,
                      complemento AS complement,
                      pais        AS country,
                      'comercial' AS address_type
                    FROM Jurid_CliFor AS CLIFOR_END
                    WHERE CLIFOR_END.Status = 'Ativo' AND CLIFOR_END.Razao IS NOT NULL AND CLIFOR_END.Razao <> ''
                          AND (endereco IS NOT NULL OR cidade IS NOT NULL OR bairro IS NOT NULL OR uf IS NOT NULL)
                    UNION
                    SELECT
                      codigo          AS person__legacy_code,
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
                          AND (Cob_endereco IS NOT NULL OR Cob_Cidade IS NOT NULL OR Cob_Bairro IS NOT NULL OR Cob_UF IS NOT NULL)
                    """
    has_status = False

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        """
        Metodo responsavel por importar os dados referente aos enderecos das pessoas
        cadastradas no advwin para o EZL
        :param rows: Enderecos lidos do advwin
        :param user: Usuario do django responsavel por persistir os dados
        :param rows_count: Quantidade de dados que foram lidos do advwin
        """
        for row in rows:
            rows_count -= 1
            try:
                legacy_code = row['person__legacy_code']
                persons = Person.objects.filter(
                  legacy_code=legacy_code, 
                  legacy_code__isnull=False,
                  offices=default_office,
                  system_prefix=LegacySystem.ADVWIN.value)
                address_type_name = 'Cobrança'
                if row['address_type'] == 'comercial':
                    address_type_name = 'Comercial'
                address_type, created = AddressType.objects.get_or_create(name=address_type_name,
                                                                          create_user=user)
                for person in persons:
                    country = Country.objects.filter(
                        name__unaccent__iexact=row['country'].strip() if row[
                            'country'] else '') or Country.objects.filter(
                        name__unaccent__iexact='Brasil')
                    state = State.objects.filter(
                        initials__iexact=row['state'].strip() if row[
                            'state'] else '') or State.objects.filter(
                        name__iexact='ESTADO-INVÁLIDO')
                    city = City.objects.filter(
                        name__unaccent__iexact=row['city'].strip() if row[
                            'city'] else '') or City.objects.filter(
                        name__unaccent__iexact='CIDADE-INVÁLIDO')
                    # Tratamento feito pelo fato de existir cadastros no advwin com cidade mas
                    # sem estado. Alem disso pode ocorrer de exisitr cidade em mais de um estado
                    # Como Sao Francisco por exemplo.
                    if state and city.count() > 1:
                        city = city.filter(state=state)
                    state = state.first()
                    if state.name == 'ESTADO-INVÁLIDO' and city:
                        state = city.first().state
                    address = Address.objects.filter(
                        person=person,
                        street=row['street'] or '',
                        number=row['number'] or '',
                        city=city,
                        complement=row['complement'] or '',
                        city_region=row['city_region'] or '',
                        zip_code=row['zip_code'] or ''
                    )
                    if not address:
                        obj = self.model(person=person,
                                         street=row['street'] or '',
                                         number=row['number'] or '',
                                         complement=row['complement'] or '',
                                         city_region=row['city_region'] or '',
                                         zip_code=row['zip_code'] or '',
                                         address_type=address_type,
                                         state=state,
                                         city=city.first(),
                                         country=country.first(),
                                         alter_user=user,
                                         create_user=user)
                        obj.save()
                    self.debug_logger.debug(
                        "Endereco,%s,%s,%s,%s,%s,%s,s,%s,%s,%s,%s,%s,%s,%s" % (
                            str(person.id), str(row['street'] or '', ), str(row['number'] or ''),
                            str(row['complement'] or ''),
                            str(row['city_region'] or ''), str(row['zip_code'] or ''),
                            str(address_type.id), str(state.id), str(city.first().id),
                            str(country.first().id), str(user.id), str(user.id), self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)

if __name__ == '__main__':
    AddressETL().import_data()
