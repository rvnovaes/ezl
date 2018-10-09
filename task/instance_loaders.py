from import_export.instance_loaders import BaseInstanceLoader


class TaskModelInstanceLoader(BaseInstanceLoader):
    """
    Instance loader for Task model.

    Lookup for model instance by ``import_id_fields`` using non Null values for import_id_fields.
    """

    def get_queryset(self):
        return self.resource._meta.model.objects.all()

    def get_instance(self, row):
        try:
            params = {}
            for key in self.resource.get_import_id_fields():
                field = self.resource.fields[key]
                params[field.attribute] = field.clean(row)
                params['{}__isnull'.format(field.attribute)] = False
            return self.get_queryset().filter(office=row['office']).exclude(
                legacy_code='').get(**params)
        except self.resource._meta.model.DoesNotExist:
            return None
