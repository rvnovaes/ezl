from core.utils import LegacySystem
from etl.advwin_ezl.advwin_ezl import GenericETL
from task.models import TypeTask, SurveyType

survey_dict = {'audienciaCorrespondente': 'COURTHEARING',
               'diligenciaCorrespondente': 'DILIGENCE', 'protocoloCorrespondente': 'PROTOCOL',
               'alvaraCorrespondente': 'OPERATIONLICENSE'}


class TypeTaskETL(GenericETL):
    model = TypeTask
    query = "SELECT  tm.Codigo,  tm.Descricao, tm.formulario_id FROM Jurid_CodMov AS tm  " \
            "WHERE right(tm.Codigo, 1) <> '.'  " \
            "   AND (tm.UsarOS = 1 AND tm.UsarOS IS NOT NULL)  " \
            "   AND tm.Status = 'Ativo'  " \
            "   AND tm.Codigo= (SELECT MIN(tm2.codigo)    " \
            "                   FROM Jurid_CodMov AS tm2 WHERE tm.Descricao = tm2.Descricao)"
    advwin_table = 'Jurid_CodMov'
    has_status = True

    def load_etl(self, rows, user, rows_count):
        for row in rows:
            code = row['Codigo']
            name = row['Descricao']
            survey_key = row['formulario_id']
            key = survey_dict[survey_key]
            survey_type = SurveyType[key].name.title()

            # tem que verificar se é novo antes para não salvar o create_user ao fazer update
            instance = self.model.objects.filter(legacy_code=code,
                                                 system_prefix=LegacySystem.ADVWIN.value).first()
            if instance:
                instance.name = name
                instance.survey_type = survey_type
                instance.alter_user = user
                instance.is_active = True
                instance.save(update_fields=['is_active', 'name', 'alter_user', 'alter_date', 'survey_type'])
            else:
                self.model.objects.create(name=name,
                                          is_active=True,
                                          legacy_code=code,
                                          survey_type=survey_type,
                                          system_prefix=LegacySystem.ADVWIN.value,
                                          create_user=user,
                                          alter_user=user)
        super(TypeTaskETL, self).load_etl(rows, user, rows_count)


if __name__ == "__main__":
    TypeTaskETL().import_data()
