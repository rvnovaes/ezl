from import_export import resources
from task.models import Task


class TaskResource(resources.ModelResource):
    folder_number =
    class Meta:
        model = Task

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        if 'id' not in dataset._Dataset__headers:
            dataset.insert_col(0, col=["", ] * dataset.height, header="id")
        dataset.insert_col(1, col=["{}".format(kwargs['office'].id), ] * dataset.height, header="office")
        dataset.insert_col(1, col=["{}".format(kwargs['create_user'].id), ] * dataset.height, header="create_user")
