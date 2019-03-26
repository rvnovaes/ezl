from django.core.management.base import BaseCommand
from core.models import Office
from manager.template_values import ListTemplateValues
from manager.enums import *
import logging

logger = logging.getLogger('test_migration_custom_settings')


class Command(BaseCommand):
    help = 'Check if the migration command for custom_settings is ok'

    def handle(self, *args, **options):
        logger.info('Iniciando teste')
        error_list = []
        for office in Office.objects.all():
            if getattr(office, 'customsettings', None):
                manager = ListTemplateValues(office)
                office_check_list = []
                office_check_list.append({
                    'value': office.customsettings.default_customer,
                    'office_id': office.id,
                    'template_key': TemplateKeys.DEFAULT_CUSTOMER.name,
                    'template_type': TypeTemplate.FOREIGN_KEY.name
                })
                office_check_list.append({
                    'value': office.customsettings.email_to_notification,
                    'office_id': office.id,
                    'template_key': TemplateKeys.EMAIL_NOTIFICATION.name,
                    'template_type': TypeTemplate.LONG_TEXT.name
                })
                office_check_list.append({
                    'value': office.use_service_old,
                    'office_id': office.id,
                    'template_key': TemplateKeys.USE_SERVICE.name,
                    'template_type': TypeTemplate.BOOLEAN.name
                })
                office_check_list.append({
                    'value': office.use_etl_old,
                    'office_id': office.id,
                    'template_key': TemplateKeys.USE_ETL.name,
                    'template_type': TypeTemplate.BOOLEAN.name
                })
                office_check_list.append({
                    'value': office.customsettings.i_work_alone,
                    'office_id': office.id,
                    'template_key': TemplateKeys.I_WORK_ALONE.name,
                    'template_type': TypeTemplate.BOOLEAN.name
                })
                office_check_list.append({
                    'value': office.customsettings.default_user,
                    'office_id': office.id,
                    'template_key': TemplateKeys.DEFAULT_USER.name,
                    'template_type': TypeTemplate.FOREIGN_KEY.name
                })
                try:
                    assert office_check_list == manager.list_template_values
                except Exception:
                    fields_error = []
                    for idx, val in enumerate(office_check_list):
                        if office_check_list[idx] != manager.list_template_values[idx]:
                            fields_error.append({'field': val.get('template_key'),
                                                 'old_value': val.get('value'),
                                                 'new_value': manager.list_template_values[idx].get('value')})
                    error_list.append({'office_id': office.id,
                                       'legal_name': office.legal_name,
                                       'fields': fields_error})
            else:
                fields_error = [{'field': 'customsettings',
                                 'old_value': 'Office não possui custom_settings',
                                 'new_value': None}]
                error_list.append({'office_id': office.id,
                                   'legal_name': office.legal_name,
                                   'fields': fields_error})
        assert error_list.__len__() == 0, 'Foram encontrados {} erros na migracao do custom_settings: {}'.format(
            error_list.__len__(),
            error_list)
