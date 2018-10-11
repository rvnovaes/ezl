import datetime
from core.models import Person
from django.utils.timezone import make_aware
from import_export.widgets import ForeignKeyWidget, Widget, DateTimeWidget
from task.models import TaskStatus
from task.messages import *
from codemirror import CodeMirrorTextarea

code_mirror_schema = CodeMirrorTextarea(
    mode="javascript",
    theme="material",
    config={
        'fixedGutter': True,
        'indentUnit': 4
    })


class UnaccentForeignKeyWidget(ForeignKeyWidget):
    """
    Widget to find foreginkey records based on unaccent text.
    """

    def clean(self, value, row=None, *args, **kwargs):
        val = super(ForeignKeyWidget, self).clean(value)
        if val:
            ret = self.get_queryset(value, row, *args, **kwargs).filter(**{'{}'.format(self.field): val}).first()
            return ret if ret else self.get_queryset(
                value, row, *args, **kwargs).filter(
                    **{
                        '{}__unaccent__iexact'.format(self.field): val
                    }).first()
        else:
            return None

    def get_queryset(self, value, row, *args, **kwargs):
        try:
            office_field = self.model._meta.get_field('office')
            return self.model.objects.get_queryset(office=row['office'])
        except:
            return super().get_queryset(value, row, *args, **kwargs)


class PersonAskedByWidget(UnaccentForeignKeyWidget):
    """
    Widget to find the person_asked_by.
    """

    def clean(self, value, row=None, *args, **kwargs):
        person_asked_by = super().clean(value)
        if person_asked_by and person_asked_by in Person.objects.requesters(
                office_id=row['office']):
            return person_asked_by
        else:
            raise ValueError(
                "Não foi encontrado solicitante para este escritório com o nome {}."
                .format(value))


class TaskStatusWidget(Widget):
    """
    Widget to get task_status from TaskStatus enum
    """

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            values = [item.value.title() for item in TaskStatus]
            if value.title() in values:
                ret = TaskStatus._value2member_map_.get(value)
            else:
                raise ValueError(WRONG_TASK_STATUS.format(value.title(), values))
        else:
            ret = TaskStatus.REQUESTED
        return ret


class DateTimeWidgetMixin(DateTimeWidget):
    """
    Widget to convert from excell double to string datetime
    """

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        if isinstance(value, float):
            seconds = int(round((value - 25569) * 86400.0))
            value = make_aware(datetime.datetime.utcfromtimestamp(seconds))
        return super().clean(value, row, *args, **kwargs)
