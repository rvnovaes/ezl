# TODO: Mover odas as constantes para as classes ou módulos onde elas pertencem.

CREATE_SUCCESS_MESSAGE = 'Registro criado com sucesso'

UPDATE_SUCCESS_MESSAGE = 'Registro atualizado com sucesso'

ADDRESS_UPDATE_SUCCESS_MESSAGE = 'Endereço atualizado com sucesso.'

ADDRESS_UPDATE_ERROR_MESSAGE = 'Erro ao atualizar o endereço.'

ERROR_FILE_EXITS_MESSAGE = 'Erro: impossível encontrar o arquivo.'

DELETE_EXCEPTION_MESSAGE = 'Erro: impossível excluir o arquivo.'

DELETE_SUCCESS_MESSAGE = 'Registros selecionados de {} excluídos com sucesso'

NO_PERMISSIONS_DEFINED = 'Não existem permissões de acesso definidas para este usuário, por isso não será exibida nenhuma providência!'


def delete_error_protected(model_name, related_model):
    return ('Não é possível excluir o(s) registros de ' +
            model_name +
            ' porque existem registros '
            'associados em outra parte do sistema!'
            ' A exclusão será cancelada.')


def success_delete():
    return 'Arquivo excluído com sucesso !'


def success_sent():
    return 'Arquivo(s) enviado(s) com sucesso.'


def operational_error_create():
    return 'Erro: ocorreu algo inesperado ao importar o arquivo.'


def ioerror_create():
    return 'Erro: impossível importar o arquivo.'


def exception_create():
    return 'Ocorreu um erro ao importar o arquivo.'


def integrity_error_delete():
    return 'Erro: impossível excluir o arquivo.'
