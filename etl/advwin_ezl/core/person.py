from django.contrib.auth.models import Group
from core.models import Person, OfficeMembership
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.utils import get_message_log_default, save_error_log


class PersonETL(GenericETL):
    model = Person
    import_query = """
                    SELECT a1.nome   AS legal_name,
                           a1.nome   AS name,
                           a1.codigo AS legacy_code,
                           'N/D'     AS legal_type,
                           'F'       AS customer_supplier,
                           'True'    AS is_lawyer,
                           CASE a1.correspondente
                             WHEN 0 THEN 'False'
                             ELSE 'True'
                           END       AS is_correspondent,
                           a1.Status
                    FROM   {advogado} AS a1
                    WHERE  a1.status = 'Ativo'
                           AND a1.nome IS NOT NULL
                           AND a1.nome <> ''
                    UNION
                    SELECT cf.razao  AS legal_name,
                           cf.nome   AS name,
                           cf.codigo AS legacy_code,
                           CASE cf.pessoa_fisica
                             WHEN 0 THEN 'J'
                             ELSE 'F'
                           END       AS legal_type,
                           cf.tipocf AS customer_supplier,
                           'False'   AS is_lawyer,
                           'False'   AS is_correspondent,
                           CASE cf.tipocf
                             WHEN 'C' THEN cf.Status
                             WHEN 'F' THEN cf.StatusFornecedor
                             ELSE cf.Status
                           END       AS Status
                    FROM   {clifor} AS cf
                    WHERE  ((cf.tipocf = 'C' and Status = 'Ativo') OR
                    	   (cf.tipocf = 'F' and StatusFornecedor = 'Ativo') OR
						   (cf.tipocf = 'A' and Status = 'Ativo' and StatusFornecedor = 'Ativo'))
                           AND cf.razao IS NOT NULL
                           AND cf.razao <> ''
                """.format(
        tribunal='Jurid_Tribunais',
        advogado='Jurid_Advogado',
        clifor='Jurid_Clifor')

    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, default_office, log=False):
        """
        Metodo responsavel por importar as pessoas cadastradas no advwin para o ezl
        :param rows: Pessoas lidas do advwin
        :param user: Usuario do django responsavel por persistir os dados
        :param rows_count: Quantidade de dados que foram lidos do advwin
        """
        correspondent_group, nil = Group.objects.get_or_create(
            name=Person.CORRESPONDENT_GROUP)

        for row in rows:
            rows_count -= 1
            try:
                legal_name = row['legal_name'] or row['name']
                name = row['name'] or row['legal_name']
                legacy_code = row['legacy_code']
                legal_type = row['legal_type']
                customer_supplier = row['customer_supplier']
                is_lawyer = row['is_lawyer']
                cpf_cnpj = None
                if legal_type != 'F' and legal_type != 'J':
                    if str(legacy_code).isnumeric():
                        # se for maior que 11 provavelmente é o cnpj
                        if len(legacy_code) > 11:
                            legal_type = 'J'
                        else:
                            legal_type = 'F'
                    else:
                        # se nao der pra saber se é pessoa fisica ou juridica será considerada
                        # juridica
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

                instance = self.model.objects.filter(
                    legacy_code=legacy_code,
                    legacy_code__isnull=False,
                    offices=default_office,
                    system_prefix=LegacySystem.ADVWIN.value).first()
                if instance:
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    update_fields = [
                        'alter_date', 'legal_name', 'name', 'legal_type',
                        'cpf_cnpj', 'alter_user', 'is_active', 'is_customer',
                        'is_supplier'
                    ]
                    instance.legal_name = legal_name
                    instance.name = name
                    if not instance.is_lawyer:
                        instance.is_lawyer = is_lawyer
                        update_fields.append('is_lawyer')
                    instance.legal_type = legal_type
                    instance.cpf_cnpj = cpf_cnpj
                    instance.alter_user = user
                    instance.is_customer = is_customer
                    instance.is_supplier = is_supplier
                    instance.is_active = is_active
                    instance.save(update_fields=update_fields)
                    if not default_office.persons.filter(pk=instance.pk):
                        OfficeMembership.objects.update_or_create(
                            person=instance,
                            office=default_office,
                            defaults={
                                'create_user': user,
                                'is_active': is_active
                            })
                else:
                    obj = self.model(
                        legal_name=legal_name,
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
                        system_prefix=LegacySystem.ADVWIN.value)

                    obj.save()
                    if not default_office.persons.filter(pk=obj.pk):
                        OfficeMembership.objects.create(
                            person=obj,
                            office=default_office,
                            create_user=user,
                            is_active=is_active)

                self.debug_logger.debug(
                    'Pessoa,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s'
                    % (str(legal_name), str(name), str(is_lawyer),
                       str(legal_type), str(cpf_cnpj), str(user.id),
                       str(user.id), str(is_customer), str(is_supplier),
                       str(is_active), str(legacy_code),
                       str(LegacySystem.ADVWIN.value), self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == '__main__':
    PersonETL().import_data()
