from enum import Enum


class ChoiceEnum(Enum):

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class CategoryPrice(ChoiceEnum):
    """
    Este enumerador é usado para cadastrar a categoria da política de preço, na tabela de preço, e também é utilizado
    na tabela de Task, para dizer a categoria do preço selecionado para a OS.
    """
    DEFAULT = 'Padrão'
    PUBLIC = 'Público'
    NETWORK = 'Rede'

    def __str__(self):
        return self.name


class BillingMoment(ChoiceEnum):
    PRE_PAID = 'Pré-pago'
    POST_PAID = 'Pós-pago'

    def __str__(self):
        return self.name


class RateType(ChoiceEnum):
    PERCENT = 'Percentual'
    VALUE = 'Valor'

    def __str__(self):
        return self.name
