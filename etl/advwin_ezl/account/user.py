# esse import deve vir antes de todos porque ele executa o __init__.py
from django.contrib.auth.models import User
from django.utils import timezone
from etl.advwin_ezl.advwin_ezl.signals import new_person

from core.models import Person
from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL


class UserETL(GenericETL):
    advwin_table = 'ADVWeb_usuario'
    model = User
    query = "SELECT  u1.usuarioLogin AS username," \
            "u1.usuarioNome AS name_user, " \
            "u1.usuarioEmail AS email, " \
            "a1.Razao AS legal_name, " \
            "a1.Nome AS name, " \
            "a1.Codigo AS legacy_code, 'True' AS is_lawyer, 'True' AS is_correspondent, 'False' AS is_court" \
            " FROM (" + advwin_table + " AS u1" \
            " INNER JOIN Jurid_Advogado AS a1 ON u1.codigo_adv = a1.Codigo)" \
            " WHERE  a1.Correspondente = 1 AND  u1.status = 'A' AND " \
            "u1.usuarioNome IS NOT NULL AND " \
            "u1.usuarioNome <> '' AND " \
            "u1.usuarioLogin IS NOT NULL AND " \
            "u1.usuarioLogin <> '' AND " \
            "u1.usuarioId = (SELECT min(u2.usuarioId) FROM " + advwin_table + " AS u2" \
            " WHERE u2.status = 'A' AND " \
            "u2.usuarioNome IS NOT NULL AND u2.usuarioNome <> '' AND " \
            "u2.usuarioLogin IS NOT NULL AND u2.usuarioLogin <> '' AND " \
            "u1.usuarioLogin = u2.usuarioLogin)"

    # como não tem o nosso model de usuario não tem como herdar de LegacyCode e não tem como inativar os que são advwin
    # todo: fazer model de usuario pra ter herança com LegacyCode e Audit
    # has_status = True

    def load_etl(self, rows, user, rows_count):
        for row in rows:
            created = False
            person_id = None

            print(rows_count)
            rows_count -= 1

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
            is_lawyer = row['is_lawyer']
            is_correspondent = row['is_correspondent']
            is_court = row['is_court']

            # maxlength = 30 no auth_user do django
            first_name = (name_user.split(' ')[0])[:30]
            last_name = (" ".join(name_user.split(' ')[1:]))[:30]

            # tenta encontrar o usuario pelo username (unique)
            instance = User.objects.filter(username=username).first() or None

            # todo: fazer usuario independente do usuario do django (extend, override or custom user???)
            # todo: deve herdar de LegacyCode e Audit e já deve criar person ao criar o usuário
            # tenta encontrar a pessoa pelo legacy_code
            person = Person.objects.filter(legacy_code=legacy_code,
                                           system_prefix=LegacySystem.ADVWIN.value).first()

            if instance:
                person = Person.objects.filter(legacy_code=legacy_code, auth_user=instance,
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

            elif not person and not instance:
                created = True
                # deve ser usada a funcao create_user para gerar a senha criptografada
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

            new_person.send(sender=self,
                            person=Person(
                                id=person_id,
                                legal_name=legal_name,
                                name=name,
                                is_lawyer=is_lawyer,
                                is_correspondent=is_correspondent,
                                is_court=is_court,
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

            super(UserETL, self).load_etl(rows, user, rows_count)


if __name__ == "__main__":
    UserETL().import_data()
