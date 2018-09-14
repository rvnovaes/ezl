from __future__ import unicode_literals

from django.db import migrations


def create_service_price_table_ezlog(apps, schema_editor):
    from django.db.models import Max
    from financial.models import ServicePriceTable
    from core.models import Office
    from django.contrib.auth.models import User
    create_user = User.objects.filter(username='admin').first()
    if not create_user:
        return True

    price_filters = ServicePriceTable.objects.filter(office_id=1, client=None, value__gt=0).values('type_task',
                                                                                                   'court_district',
                                                                                                   'state')
    ezlog_office = Office.objects.filter(legal_name='EZLog').first()
    for price_filter in price_filters:
        type_task_id = price_filter.get('type_task')
        court_district_id = price_filter.get('court_district')
        state_id = price_filter.get('state')
        max_value = ServicePriceTable.objects.filter(type_task_id=type_task_id, court_district_id=court_district_id,
                                                     state_id=state_id, client=None, value__gt=0.0).aggregate(
            Max('value'))
        max_value = max_value.get('value__max') * 2
        ServicePriceTable.objects.get_or_create(
            office=ezlog_office,
            office_correspondent=ezlog_office,
            type_task_id=type_task_id,
            court_district_id=court_district_id,
            state_id=state_id, defaults={
                'create_user': create_user,
                'client': None,
                'value': max_value
            })


class Migration(migrations.Migration):
    dependencies = [
        ('financial', '0016_remove_servicepricetable_correspondent')
    ]

    operations = [
        migrations.RunPython(create_service_price_table_ezlog)
    ]
