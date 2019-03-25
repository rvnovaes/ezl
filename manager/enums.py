from enum import Enum


class TypeTemplate(Enum):
    BOOLEAN = 'Boleano'
    SIMPLE_TEXT = 'Texto Simples'
    LONG_TEXT = 'Texto Longo'
    FOREIGN_KEY = 'Chave estrangeira'
    INTEGER = 'Inteiro'
    DECIMAL = 'Decimal'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        choices = [(x.name, x.value) for x in cls]
        choices.sort(key=lambda tup: tup[1])
        return choices


class TemplateKeys(Enum):
    DEFAULT_CUSTOMER = 'Cliente padrão'
    DEFAULT_USER = 'Usuário padrão'
    EMAIL_NOTIFICATION = 'E-mail de notificação'
    USE_SERVICE = 'Equipe conferência dados'
    USE_ETL = 'Importa dados de outros sistemas'
    I_WORK_ALONE = 'Trabalho sozinho'

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        choices = [(x.name, x.value) for x in cls]
        choices.sort(key=lambda tup: tup[1])
        return choices