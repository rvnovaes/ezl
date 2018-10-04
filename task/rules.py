from core.models import Team
from django.db.models import Q
from core.utils import get_office_session
from task.models import TaskStatus


class RuleViewTask(object):
    """
    Classe reponsavel por gerar os filtros das tasks de acordo com o 
    perfil do usuario
    """

    def __init__(self, request):
        self.request = request

    @staticmethod
    def get_query_all_tasks(person):
        return Q()

    @staticmethod
    def get_query_delegated_tasks(person):
        return Q(person_executed_by=person.id)

    @staticmethod
    def get_query_requested_tasks(person):
        return Q(person_asked_by=person.id)

    @staticmethod
    def get_query_distributed_tasks(person):
        return Q(task_status=TaskStatus.REQUESTED) | Q(
            task_status=TaskStatus.ERROR) | Q(person_distributed_by=person.id)

    @staticmethod
    def get_query_team_tasks_to_user(person):
        teams = Team.objects.filter(
            supervisors=person.auth_user, is_active=True)
        members = Team.objects.none()
        for team in teams:
            members |= team.members.all()
        if not teams:
            return Q()
        return Q(person_asked_by__auth_user__in=members) | Q(
            person_distributed_by__auth_user__in=members) | Q(
                person_executed_by__auth_user__in=members)

    @staticmethod
    def get_query_team_tasks(teams):
        members = Team.objects.none()
        for team in teams:
            members |= team.members.all()
        if not teams:
            return Q()
        return Q(person_asked_by__auth_user__in=members) | Q(
            person_distributed_by__auth_user__in=members) | Q(
                person_executed_by__auth_user__in=members)

    def get_dynamic_query(self, person, checker):
        dynamic_query = Q()
        office_session = get_office_session(self.request)
        if office_session:
            if checker.has_perm('view_all_tasks', office_session):
                return self.get_query_all_tasks(person)
            permissions_to_check = {
                'view_all_tasks':
                self.get_query_all_tasks,
                'view_delegated_tasks':
                self.get_query_delegated_tasks,
                'view_distributed_tasks':
                self.get_query_distributed_tasks,
                'view_requested_tasks':
                self.get_query_requested_tasks,
                'can_see_tasks_from_team_members':
                self.get_query_team_tasks_to_user,
            }
            for permission in checker.get_perms(office_session):
                if permission in permissions_to_check.keys():
                    dynamic_query |= permissions_to_check.get(permission)(
                        person)
        return dynamic_query
