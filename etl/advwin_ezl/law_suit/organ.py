#!/usr/bin/python
# -*- encoding: utf-8 -*-

from lawsuit.models import CourtDistrict, Organ
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.factory import InvalidObjectFactory
from etl.utils import get_message_log_default, save_error_log


class OrganETL(GenericETL):
    model = Organ
    import_query = """
                    SELECT t1.descricao AS legal_name,
                           t1.descricao AS name,
                           t1.codigo    AS legacy_code,
                           t1.Comarca   AS court_district
                    FROM   {tribunal} AS t1
                    WHERE  t1.descricao IS NOT NULL
                           AND t1.descricao <> ''
                           AND t1.codigo = (SELECT Min(t2.codigo)
                                            FROM   {tribunal} AS t2
                                            WHERE  t2.descricao IS NOT NULL
                                                   AND t2.descricao <> ''
                                                   AND t1.codigo = t2.codigo)
                """.format(tribunal='Jurid_Tribunais')

    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        """
        Metodo responsavel por importar as pessoas cadastradas no advwin para o ezl
        :param rows: Pessoas lidas do advwin
        :param user: Usuario do django responsavel por persistir os dados
        :param rows_count: Quantidade de dados que foram lidos do advwin
        """
        for row in rows:
            rows_count -= 1
            try:
                legal_name = row['legal_name'] or row['name']
                name = row['name'] or row['legal_name']
                legacy_code = row['legacy_code']
                legal_type = 'J'
                is_lawyer = False
                cpf_cnpj = None
                if str(legacy_code).isnumeric() and len(legacy_code) == 14:
                    # no advwin nao tem campo para cpf_cnpj, é salvo no codigo
                    cpf_cnpj = legacy_code
                is_customer = False
                is_supplier = True
                is_active = True
                instance = self.model.objects.filter(legacy_code=legacy_code,
                                                     system_prefix=LegacySystem.ADVWIN.value).first()
                court_district = CourtDistrict.objects.filter(
                    name__unaccent__iexact=row[
                        'court_district']).first() or InvalidObjectFactory.get_invalid_model(
                    CourtDistrict)
                if instance:
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    instance.legal_name = legal_name
                    instance.name = name
                    instance.is_lawyer = is_lawyer
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
                                       'legal_type',
                                       'cpf_cnpj',
                                       'alter_user',
                                       'is_active',
                                       'is_customer',
                                       'is_supplier',
                                       'court_district'])
                else:
                    obj = self.model(legal_name=legal_name,
                                     name=name,
                                     is_lawyer=is_lawyer,
                                     legal_type=legal_type,
                                     cpf_cnpj=cpf_cnpj,
                                     alter_user=user,
                                     create_user=user,
                                     is_customer=is_customer,
                                     is_supplier=is_supplier,
                                     is_active=is_active,
                                     legacy_code=legacy_code,
                                     system_prefix=LegacySystem.ADVWIN.value,
                                     court_district=court_district)

                    obj.save()
                self.debug_logger.debug(
                    "Pessoa,%s,%s,%s,%s,%s,%s,s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                        str(legal_name), str(name), str(is_lawyer), str(legal_type), str(cpf_cnpj),
                        str(user.id), str(user.id), str(is_customer), str(is_supplier),
                        str(is_active), str(legacy_code), str(court_district),
                        str(LegacySystem.ADVWIN.value), self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == "__main__":
    OrganETL().import_data()
