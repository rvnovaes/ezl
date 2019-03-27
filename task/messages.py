COLUMNS_NOT_AVAILABLE = "A coluna '{}' não foi encontrada no dataset. As colunas disponíveis são: {};"

COLUMN_ERROR = "Coluna '{}': {};"

INCORRECT_NATURAL_KEY = "Não existe {} com o valor informado para a coluna {} - {};"

REQUIRED_COLUMN = "A coluna {} é de preenchimento obrigatório;"

REQUIRED_COLUMN_RELATED = "A coluna {} é deve ser preenchida com um valor válido caso a coluna {} esteja preenchida;"

REQUIRED_ONE_IN_GROUP = "É obrigatório o preenchimento de um dos campos de {} ({});"

RECORD_NOT_FOUND = "Não foi encontrado registro de {} correspondente aos valores informados;"

WRONG_TASK_STATUS = "{} não é um valor de status válido: {}."

DEFAULT_CUSTOMER_MISSING = "O escritório {} não possui cliente padrão configurado"

MISSING_ACCEPTANCE_SERVICE_DATE = "A data de aceite pelo service é obrigatória caso o status da OS seja " \
                                  "Aceita pelo Service"

MIN_HOUR_ERROR = 'O prazo de cumprimento da OS é inferior a {} horas.'


def columns_not_available(column, columns_list):
    return COLUMNS_NOT_AVAILABLE.format(column, columns_list)


def column_error(column, error):
    return COLUMN_ERROR.format(column, error)


def incorrect_natural_key(verbose_name, column_name, value):
    return INCORRECT_NATURAL_KEY.format(verbose_name,
                                        column_name,
                                        value)


def required_one_in_group(group_name, fields):
    return REQUIRED_ONE_IN_GROUP.format(group_name, fields)


def record_not_found(record_model):
    return RECORD_NOT_FOUND.format(record_model)


def required_column(column):
    return REQUIRED_COLUMN.format(column)


def required_column_related(column, column_related):
    return REQUIRED_COLUMN_RELATED.format(column, column_related)


def wrong_task_status(status, valid_status):
    return WRONG_TASK_STATUS.format(status, valid_status)


def default_customer_missing(office):
    return DEFAULT_CUSTOMER_MISSING.format(office)


def min_hour_error(min_hour):
    return MIN_HOUR_ERROR.format(min_hour)
