from import_export.instance_loaders import BaseInstanceLoader


class TaskModelInstanceLoader(BaseInstanceLoader):
    """
    Instance loader for Task model.

    Lookup for model instance by ``import_id_fields`` using non Null values for import_id_fields.
    """

    def get_queryset(self):
        return self.resource._meta.model.objects.all()

    def get_instance(self, row):
        ret = None
        for key in self.resource.get_import_id_fields():
            params = {}
            field = self.resource.fields[key]
            params[field.attribute] = field.clean(row)
            params['{}__isnull'.format(field.attribute)] = False
            instance = self.get_queryset().filter(office=row['office']).exclude(
                legacy_code='').filter(**params).first()
            if instance:
                row['id'] = instance.id
                row['task_number'] = instance.task_number
                if instance.legacy_code:
                    row['legacy_code'] = instance.legacy_code
                ret = instance
                break

        return ret
