# esse import deve vir antes de todos porque ele executa o __init__.py
from etl.advwin.advwin_ezl.advwin_ezl import GenericETL

from django.utils import timezone

from django.contrib.auth.models import User
from core.models import Person
from core.utils import LegacySystem


class UserETL(GenericETL):
    advwin_table = 'ADVWeb_usuario'
    model = User
    query = "select \n" \
            "  u1.usuarioLogin as username, \n" \
            "  u1.usuarioNome as name_user, \n" \
            "  u1.usuarioEmail as email, \n" \
            "  a1.Razao as legal_name, \n" \
            "  a1.Nome as name, \n" \
            "  a1.Codigo as legacy_code, \n" \
            "  'True' as is_lawyer, \n" \
            "  'True' as is_correspondent, \n" \
            "  'False' as is_court \n" \
            "from (" + advwin_table + " as u1 \n" \
            "INNER JOIN Jurid_Advogado as a1 on \n" \
            "  u1.codigo_adv = a1.Codigo) \n" \
            "where \n" \
            "  a1.Correspondente = 1 and \n" \
            "  u1.status = 'A' and \n" \
            "  u1.usuarioNome is not null and u1.usuarioNome <> '' and \n" \
            "  u1.usuarioLogin is not null and u1.usuarioLogin <> '' and \n" \
            "  u1.usuarioId = ( \n" \
            "  select min(u2.usuarioId) \n" \
            "  from " + advwin_table + " as u2 \n" \
            "  where \n" \
            "    u2.status = 'A' and \n" \
            "    u2.usuarioNome is not null and u2.usuarioNome <> '' and \n" \
            "    u2.usuarioLogin is not null and u2.usuarioLogin <> '' and \n" \
            "    u1.usuarioLogin = u2.usuarioLogin)"

    # como não tem o nosso model de usuario não tem como herdar de LegacyCode e não tem como inativar os que são advwin
    # todo: fazer model de usuario pra ter herança com LegacyCode e Audit
    # has_status = True

    def load_etl(self, rows, user):
        for row in rows:
            print(row)

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

            if str(legacy_code).isnumeric():
                if len(legacy_code) > 11:
                    legal_type = 'J'
                else:
                    legal_type = 'F'
                # no advwin nao tem campo para cpf_cnpj, é salvo no codigo
                cpf_cnpj = legacy_code

            is_client = False
            is_provider = True
            is_lawyer = row['is_lawyer']
            is_correspondent = row['is_correspondent']
            is_court = row['is_court']

            # maxlength = 30 no auth_user do django
            first_name = (name_user.split(' ')[0])[:30]
            last_name = (" ".join(name_user.split(' ')[1:]))[:30]

            # todo: fazer usuario independente do usuario do django (extend, override or custom user???)
            # todo: deve herdar de LegacyCode e Audit e já deve criar person ao criar o usuário
            # person = Person.objects.select_related('auth_user').filter(legacy_code=legacy_code,
            #                                                            system_prefix=LegacySystem.ADVWIN.value).first()
            # tenta encontrar a pessoa pelo legacy_code
            person = Person.objects.filter(legacy_code=legacy_code,
                                           system_prefix=LegacySystem.ADVWIN.value).first()

            if person:
                # tenta encontrar o usuario vinculado a essa pessoa
                instance = self.model.objects.get(id=person.auth_user.id)
            else:
                instance = None

            if instance:
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
                                   'username',
                                   'email',
                                   'is_staff',
                                   'is_active',
                                   'date_joined',
                                   'first_name',
                                   'last_name'])

                person.legal_name = legal_name
                person.name = name
                person.is_lawyer = is_lawyer
                person.is_correspondent = is_correspondent
                person.is_court = is_court
                person.legal_type = legal_type
                person.cpf_cnpj = cpf_cnpj
                person.alter_user = user
                person.is_client = is_client
                person.is_provider = is_provider
                person.save(
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
                # deve ser usada a funcao create_user para gerar a senha criptografada
                user_obj = self.model.objects.create_user(password=password,
                                                          is_superuser=is_superuser,
                                                          username=username,
                                                          first_name=first_name,
                                                          last_name=last_name,
                                                          email=email,
                                                          is_staff=is_staff,
                                                          is_active=is_active,
                                                          date_joined=date_joined)

                person_obj = Person(legal_name=legal_name,
                                    name=name,
                                    is_lawyer=is_lawyer,
                                    is_correspondent=is_correspondent,
                                    is_court=is_court,
                                    legal_type=legal_type,
                                    cpf_cnpj=cpf_cnpj,
                                    alter_user=user,
                                    auth_user=user_obj,
                                    create_user=user,
                                    is_active=is_active,
                                    is_client=is_client,
                                    is_provider=is_provider,
                                    legacy_code=legacy_code,
                                    system_prefix=LegacySystem.ADVWIN.value)
                person_obj.save()

            super(UserETL, self).load_etl(rows, user)


if __name__ == "__main__":
    UserETL().import_data()
