from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Person, OfficeRelGroup
from task.models import Permissions
from survey.models import SurveyPermissions
from core.models import CorePermissions
from guardian.shortcuts import assign_perm, remove_perm


GROUP_PERMISSIONS = {

    Person.ADMINISTRATOR_GROUP: (
        Permissions.view_all_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        SurveyPermissions.can_edit_surveys,
        SurveyPermissions.can_view_survey_results,
        Permissions.can_distribute_tasks,
        CorePermissions.group_admin
    ),

    Person.SUPERVISOR_GROUP: (
        Permissions.can_access_settings,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        SurveyPermissions.can_edit_surveys,
        SurveyPermissions.can_view_survey_results,
        Permissions.can_distribute_tasks,
        Permissions.view_distributed_tasks,
        Permissions.view_requested_tasks,
        Permissions.view_delegated_tasks,
        Permissions.can_see_tasks_from_team_members
    ),

    Person.SERVICE_GROUP: (
        Permissions.view_distributed_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        SurveyPermissions.can_edit_surveys,
        SurveyPermissions.can_view_survey_results,
        Permissions.can_distribute_tasks
    ),

    Person.CORRESPONDENT_GROUP: (
        Permissions.view_delegated_tasks,
    ),

    Person.REQUESTER_GROUP: (
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.view_requested_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data
    ),

}


def create_permission(office):
    from core.models import Office
    content_type = ContentType.objects.get_for_model(Office)
    for group_name, permissions in GROUP_PERMISSIONS.items():
        name = '{}-{}'.format(group_name, office.id)
        group, nil = create_group(name)
        if office.legal_name == 'Marcelo Tostes Advogados Associados' and office.pk == 1:
            update_groups(group_name, group_name, office)
        update_groups(group_name, '{}-{}-{}'.format(group_name,
                                                    office.id, office.legal_name), office)
        group.permissions.clear()
        OfficeRelGroup.objects.filter(group=group).delete()
        for permission in Permissions:
            remove_perm(permission.name, group, office)
        for codename in permissions:
            permission, nil = Permission.objects.get_or_create(
                codename=codename.name,
                content_type=content_type,
                defaults={'name': codename.value}
            )
            assign_perm(codename.name, group, office)
            group.permissions.add(permission)
            OfficeRelGroup.objects.get_or_create(office=office, group=group)


def create_group(group_name):
    return Group.objects.get_or_create(name=group_name)


def update_groups(group_name, name_to_search, office):
    groups = Group.objects.filter(name=name_to_search)
    for group in groups:
        if Group.objects.filter(name='{}-{}'.format(group_name, office.id)).exists():
            old_group = Group.objects.filter(
                name='{}-{}'.format(group_name, office.id)).first()
            for user in group.user_set.all():
                old_group.user_set.add(user)
            group.user_set.clear()
            group.delete()
        else:
            group.name = '{}-{}'.format(group_name, office.id)
            group.save()
