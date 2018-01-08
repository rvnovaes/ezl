from django.db import models


class LegacySurveyType:
    OPERATIONLICENSE = 1
    COURTHEARING = 2
    DILIGENCE = 3
    PROTOCOL = 4


LEGACY_TYPES = (
    (LegacySurveyType.OPERATIONLICENSE, 'Operationlicense', 'Cumprimento de Ordem de Serviço do tipo Alvará'),
    (LegacySurveyType.COURTHEARING, 'Courthearing', 'Cumprimento de Ordem de Serviço do tipo Audiência'),
    (LegacySurveyType.DILIGENCE, 'Diligence', 'Cumprimento de Ordem de Serviço do tipo Diligência'),
    (LegacySurveyType.PROTOCOL, 'Protocol', 'Cumprimento de Ordem de Serviço do tipo Protocolo')
)


def get_legacy_type_map():
    survey_map = {}
    for pk, name, title in LEGACY_TYPES:
        survey_map[name] = pk
    return survey_map


class Survey(models.Model):

    name = models.CharField(max_length=128, verbose_name='Nome')
    data = models.TextField(
        verbose_name='Conteúdo',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Pesquisa'
