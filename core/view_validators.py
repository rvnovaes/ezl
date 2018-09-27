from core.models import OfficeMembership


def create_person_office_relation(person, user, office_session):
    member, created = OfficeMembership.objects.get_or_create(
        person=person,
        office=office_session,
        defaults={
            'create_user': user,
            'is_active': True
        })
    if not created:
        # Caso o relacionamento esteja apenas inativo
        member.is_active = True
        member.save()


def person_exists(person_cnpj, office_session):
    result = office_session.persons.filter(cpf_cnpj=person_cnpj).first() \
        if person_cnpj else None
    return result
