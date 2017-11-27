# esse import deve vir antes de todos porque ele executa o __init__.py

from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone

from core.models import Person
from core.signals import create_person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from etl.advwin_ezl.signals import new_person, temp_disconnect_signal
from etl.models import ErrorETL
from etl.utils import get_message_log_default, save_error_log


class UserETL(GenericETL):
    EZL_LEGACY_CODE_FIELD = 'person__legacy_code'

    advwin_table = 'ADVWeb_usuario'
    model = User
    import_query = """
        SELECT ADVWEB_USER.usuarioLogin AS username,
              ADVWEB_USER.usuarioNome AS name_user,
              ADVWEB_USER.usuarioEmail AS email,
              ADVOGADO.Razao AS legal_name,
              ADVOGADO.Nome AS name,
              ADVOGADO.Codigo AS legacy_code
        FROM
            (ADVWeb_usuario AS ADVWEB_USER INNER JOIN Jurid_Advogado AS ADVOGADO
             ON ADVWEB_USER.codigo_adv = ADVOGADO.Codigo)
        WHERE  ADVOGADO.Correspondente = 1 AND  ADVWEB_USER.status = 'A' AND
               ADVWEB_USER.usuarioNome IS NOT NULL AND
               ADVWEB_USER.usuarioNome <> '' AND
               ADVWEB_USER.usuarioLogin IS NOT NULL AND
               ADVWEB_USER.usuarioLogin <> '' AND
               ADVWEB_USER.usuarioId =
                   (SELECT min(ADVWEB_USER2.usuarioId) FROM ADVWeb_usuario AS ADVWEB_USER2
                    WHERE ADVWEB_USER2.status = 'A' AND
                    ADVWEB_USER2.usuarioNome IS NOT NULL AND ADVWEB_USER2.usuarioNome <> '' AND
                    ADVWEB_USER2.usuarioLogin IS NOT NULL AND ADVWEB_USER2.usuarioLogin <> '' AND
                    ADVWEB_USER.usuarioLogin = ADVWEB_USER2.usuarioLogin)
            """

    # como não tem o nosso model de usuario não tem como herdar de LegacyCode e não tem como
    # inativar os que são advwin
    # todo: fazer model de usuario pra ter herança com LegacyCode e Audit
    # has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        correspondent_group, nil = Group.objects.get_or_create(name=Person.CORRESPONDENT_GROUP)

        assert len(rows) == rows_count

        for row in rows:
            created = False
            person_id = None

            print(rows_count)
            rows_count -= 1
            try:
                # todas as senhas serão importadas como 1 e o usuário terá que alterar futuramente
                password = '1'
                is_superuser = False
                name_user = row['name_user']
                email = row['email']
                if not email:
                    email = ' '
                is_staff = False
                is_active = True
                date_joined = timezone.now()
                username = row['username']
                legacy_code = row['legacy_code']
                legal_name = row['legal_name']
                name = row['name']
                legal_type = 'J'
                cpf_cnpj = None
                if str(legacy_code).isnumeric():
                    if len(legacy_code) > 11:
                        legal_type = 'J'
                    else:
                        legal_type = 'F'
                    # no advwin nao tem campo para cpf_cnpj, é salvo no codigo
                    cpf_cnpj = legacy_code

                is_customer = False
                is_supplier = True
                is_lawyer = True

                # maxlength = 30 no auth_user do django
                first_name = (name_user.split(' ')[0])[:30]
                last_name = (' '.join(name_user.split(' ')[1:]))[:30]

                # tenta encontrar o usuario pelo username (unique)
                instance = User.objects.filter(username__unaccent=username).first() or None

                # todo: fazer usuario independente do usuario do django (extend, override or
                # custom user???)
                # todo: deve herdar de LegacyCode e Audit e já deve criar person ao criar o usuário
                # tenta encontrar a pessoa pelo legacy_code
                person = Person.objects.filter(legacy_code=legacy_code,
                                               system_prefix=LegacySystem.ADVWIN.value).first()

                if instance:
                    person = Person.objects.filter(legacy_code=legacy_code,
                                                   auth_user=instance,
                                                   system_prefix=LegacySystem.ADVWIN.value).first()

                if instance and person:
                    person_id = person.id
                    if person.auth_user is None:
                        # vincula o usuario encontrado à pessoa encontrada
                        person.auth_user = instance
                elif person:
                    person_id = person.id
                    # tenta encontrar o usuario vinculado a essa pessoa
                    instance = self.model.objects.get(id=person.auth_user.id)

                if instance:
                    created = False
                    # use update_fields to specify which fields to save
                    # https://docs.djangoproject.com/en/1.11/ref/models/instances/#specifying-which-fields-to-save
                    instance.is_superuser = is_superuser
                    instance.email = email
                    instance.is_staff = is_staff
                    instance.is_active = is_active
                    instance.date_joined = date_joined
                    instance.first_name = first_name
                    instance.last_name = last_name
                    instance.save(
                        update_fields=['is_superuser',
                                       'email',
                                       'is_staff',
                                       'is_active',
                                       'date_joined',
                                       'first_name',
                                       'last_name'])

                    instance.groups.add(correspondent_group)

                elif not person and not instance:
                    created = True
                    # deve ser usada a funcao create_user para gerar a senha criptografada
                    with temp_disconnect_signal(
                            signal=models.signals.post_save,
                            receiver=create_person,
                            sender=User,
                            dispatch_uid='create_person'):

                        instance = self.model.objects.create_user(
                            password=password,
                            is_superuser=is_superuser,
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            is_staff=is_staff,
                            is_active=is_active,
                            date_joined=date_joined)

                        instance.groups.add(correspondent_group)

                    new_person.send(sender=self,
                                    person=Person(
                                        id=person_id,
                                        legal_name=legal_name,
                                        name=name,
                                        is_lawyer=is_lawyer,
                                        legal_type=legal_type,
                                        cpf_cnpj=cpf_cnpj,
                                        alter_user=user,
                                        auth_user=instance,
                                        create_user=user,
                                        is_active=is_active,
                                        is_customer=is_customer,
                                        is_supplier=is_supplier,
                                        legacy_code=legacy_code,
                                        system_prefix=LegacySystem.ADVWIN.value),
                                    created=created)

                self.debug_logger.debug(
                    'Usuario,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
                        str(person_id), str(legal_name), str(name),
                        str(is_lawyer), str(legal_type),
                        str(cpf_cnpj), str(user), str(is_active),
                        str(is_customer), str(is_customer), str(is_supplier), str(legacy_code),
                        str(LegacySystem.ADVWIN.value), self.timestr))

            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name,
                                              rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == '__main__':
    UserETL().import_data()
