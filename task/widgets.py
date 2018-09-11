from core.models import Person
from import_export.widgets import ForeignKeyWidget, Widget, DateTimeWidget
from task.models import TaskStatus


class UnaccentForeignKeyWidget(ForeignKeyWidget):
    """
    Widget to find foreginkey records based on unaccent text.
    """

    def clean(self, value, row=None, *args, **kwargs):
        val = super(ForeignKeyWidget, self).clean(value)
        if val:
            ret = self.get_queryset(value, row, *args, **kwargs).filter(
                **{'{}'.format(self.field): val}).first()
            return ret if ret else self.get_queryset(value, row, *args, **kwargs).filter(
                **{'{}__unaccent__iexact'.format(self.field): val}).first()
        else:
            return None


class PersonAskedByWidget(UnaccentForeignKeyWidget):
    """
    Widget to find the person_asked_by.
    """
    def clean(self, value, row=None, *args, **kwargs):
        person_asked_by = super().clean(value)
        if person_asked_by and person_asked_by in Person.objects.requesters(office_id=row['office']):
            return person_asked_by
        else:
            return ''


class TaskStatusWidget(Widget):
    """
    Widget to get task_status from TaskStatus enum
    """
    def clean(self, value, row=None, *args, **kwargs):
        return TaskStatus._value2member_map_.get(value, TaskStatus.REQUESTED)
