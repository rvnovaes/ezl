from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL, validate_import
from task.models import TypeTask
from survey.models import LegacySurveyType, Survey
from etl.utils import get_message_log_default, save_error_log


survey_map = {'audienciaCorrespondente': LegacySurveyType.COURTHEARING,
              'diligenciaCorrespondente': LegacySurveyType.DILIGENCE,
              'protocoloCorrespondente': LegacySurveyType.PROTOCOL,
              'alvaraCorrespondente': LegacySurveyType.OPERATIONLICENSE}


class TypeTaskETL(GenericETL):
    model = TypeTask
    import_query = """
                SELECT tm.Codigo AS legacy_code,
                       tm.Descricao,
                       tm.formulario_id

                   FROM Jurid_CodMov AS tm

                   WHERE right(tm.Codigo, 1) <> '.'
                      AND (tm.UsarOS = 1 AND tm.UsarOS IS NOT NULL)
                      AND tm.Status = 'Ativo'
                      AND tm.Codigo= (SELECT MIN(tm2.codigo)
                   FROM Jurid_CodMov AS tm2 WHERE tm.Descricao = tm2.Descricao)

                   """

    advwin_table = 'Jurid_CodMov'
    has_status = True

    @validate_import
    def config_import(self, rows, user, rows_count, log=False):
        for row in rows:

            try:
                code = row['legacy_code']
                name = row['Descricao']
                survey_key = row['formulario_id']
                survey_id = survey_map[survey_key]

                survey = Survey.objects.filter(id=survey_id)

                # tem que verificar se é novo antes para não salvar o create_user ao fazer update
                instance = self.model.objects.filter(legacy_code=code,
                                                     system_prefix=LegacySystem.ADVWIN.value).first()
                if instance:
                    instance.name = name
                    instance.survey = survey
                    instance.alter_user = user
                    instance.is_active = True
                    instance.legacy_code = code
                    instance.save(update_fields=['is_active', 'name', 'alter_user', 'alter_date', 'survey',
                                                 'legacy_code'])
                else:
                    self.model.objects.create(name=name,
                                              is_active=True,
                                              legacy_code=code,
                                              survey=survey,
                                              system_prefix=LegacySystem.ADVWIN.value,
                                              create_user=user,
                                              alter_user=user)

                self.debug_logger.debug(
                    "Type Task,%s,%s,%s,%s,%s,%s,%s,%s" % (str(name), str(True), str(code), str(survey_id),
                                                           str(LegacySystem.ADVWIN.value), str(user.id),str(user.id),
                                                           self.timestr))
            except Exception as e:
                msg = get_message_log_default(self.model._meta.verbose_name, rows_count, e, self.timestr)
                self.error_logger.error(msg)
                save_error_log(log, user, msg)


if __name__ == "__main__":
    TypeTaskETL().import_data()
