from django.core.management.base import BaseCommand
from core.models import ContactMechanism
from django.db.models import Q
from django.db.models import Count
from django.db.models.signals import post_delete, pre_delete
from task.signals import delete_ecm_advwin, delete_related_ecm
from task.models import Ecm


class Command(BaseCommand):
    help = ('Remove duplicated files from database based in two steps: 1 - not unique legacy_codes; '
            '2 - same exhibition_names')

    def handle(self, *args, **options):

        pre_delete.disconnect(delete_ecm_advwin, sender=Ecm)
        post_delete.disconnect(delete_related_ecm, sender=Ecm)

        # apaga primeiro os que tem legacy_code duplicados
        duplicate_ecms = Ecm.objects.filter(task__office_id=1,
                                            legacy_code__isnull=False).values('task_id',
                                                                              'legacy_code').annotate(
            total=Count('task_id')).order_by('-total', 'task_id')
        for duplicate in duplicate_ecms:
            task_id = duplicate['task_id']
            legacy_code = duplicate['legacy_code']
            total = duplicate['total']
            ecm_base = Ecm.objects.filter(task_id=task_id, legacy_code=legacy_code).earliest('pk')
            ecms = Ecm.objects.filter(~Q(id=ecm_base.id), Q(task_id=task_id), Q(legacy_code=legacy_code))
            if ecms.count() == total - 1:
                ids = list(ecms.values_list('id', flat=True))
                ecms = Ecm.objects.filter(id__in=ids)
                ecms.update(legacy_code=None)
                ecms.all().delete()

        # depois apaga que tem exhibition_name duplicados
        duplicate_ecms = Ecm.objects.filter(task__office_id=1).values('task_id').annotate(
            total=Count('task_id')).filter(
            total__gte=20).order_by('-total', 'task_id')
        for duplicate in duplicate_ecms:
            task_id = duplicate['task_id']
            detail_duplicate = Ecm.objects.filter(task_id=task_id).values('exhibition_name').annotate(
                total=Count('task_id')).filter(total__gt=1).order_by('-total')
            for detail in detail_duplicate:
                exhibition_name = detail['exhibition_name']
                total = detail['total']
                ecm_base = Ecm.objects.filter(task_id=task_id, exhibition_name=exhibition_name).earliest('pk')
                ecms = Ecm.objects.filter(~Q(id=ecm_base.id), Q(task_id=task_id), Q(exhibition_name=exhibition_name))
                if ecms.count() == total - 1:
                    ids = list(ecms.values_list('id', flat=True))
                    ecms = Ecm.objects.filter(id__in=ids)
                    ecms.update(legacy_code=None)
                    ecms.all().delete()
        pre_delete.connect(delete_ecm_advwin, sender=Ecm)
        post_delete.connect(delete_related_ecm, sender=Ecm)
