from import_export import resources
from task.models import Task


class TaskResource(resources.ModelResource):
    class Meta:
        model = Task
