from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Person, OfficeRelGroup
from task.models import Permissions
from survey.models import SurveyPermissions
from guardian.shortcuts import assign_perm


GROUP_PERMISSIONS = {

    Person.ADMINISTRATOR_GROUP: (
        Permissions.view_all_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        SurveyPermissions.can_edit_surveys,
        SurveyPermissions.can_view_survey_results,
        Permissions.can_distribute_tasks
    ),

    Person.SUPERVISOR_GROUP: (
        Permissions.view_all_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        SurveyPermissions.can_edit_surveys,
        SurveyPermissions.can_view_survey_results,
        Permissions.can_distribute_tasks
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
        group_name = '{}-{}'.format(group_name, office.legal_name)
        group, nil = Group.objects.get_or_create(name=group_name)
        group.permissions.clear()
        for codename in permissions:
            permission, nil = Permission.objects.get_or_create(
                codename=codename.name,
                content_type=content_type,
                defaults={'name': codename.value}
            )
            assign_perm(codename.name, group, office)
            group.permissions.add(permission)
            OfficeRelGroup.objects.get_or_create(office=office, group=group)

