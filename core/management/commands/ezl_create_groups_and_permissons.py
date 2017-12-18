from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from core.models import Person
from task.models import Permissions


GROUP_PERMISSIONS = {

    Person.ADMINISTRATOR_GROUP: (
        Permissions.view_all_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        Permissions.can_distribute_tasks
    ),

    Person.SUPERVISOR_GROUP: (
        Permissions.view_all_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
        Permissions.can_distribute_tasks
    ),

    Person.SERVICE_GROUP: (
        Permissions.view_distributed_tasks,
        Permissions.return_all_tasks,
        Permissions.validate_all_tasks,
        Permissions.block_payment_tasks,
        Permissions.can_access_general_data,
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


class Command(BaseCommand):
    help = ('Create groups and associate the task model permissions with them.')

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Person)
        for group_name, permissions in GROUP_PERMISSIONS.items():
            group, nil = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()
            for codename in permissions:
                permission, nil = Permission.objects.get_or_create(
                    codename=codename.name,
                    content_type=content_type,
                    defaults={'name': codename.value}
                )
                group.permissions.add(permission)
            print(group, group.permissions.all())
