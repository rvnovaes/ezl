new_success = "Registro criado com sucesso"
update_success = "Registro atualizado com sucesso"


def delete_success(model_name):
    return "Registros selecionados de " + model_name + " excluídos com sucesso"


def delete_error_protected(model_name, related_model):
    return "Não é possível excluir o(s) registros de " + model_name + " porque existem registros " \
                                                                      "associados em outra parte do sistema!" \
                                                                      " A exclusão será cancelada."


# GED

def success_delete():
    return "Arquivo excluído com sucesso !"


def success_sent():
    return "Arquivo(s) enviado(s) com sucesso."


def operational_error_create():
    return "Erro: ocorreu algo inesperado ao importar o arquivo."


def ioerror_create():
    return "Erro: impossível importar o arquivo."


def exception_create():
    return "Ocorreu um erro ao importar o arquivo."


def integrity_error_delete():
    return "Erro: impossível excluir o arquivo."


def file_exists_error_delete():
    return "Erro: impossível encontrar o arquivo."


def exception_delete():
    return "Erro: impossível excluir o arquivo."


def address_sucess_deleted():
    return "Endereço excluído com sucesso."


def address_error_deleted():
    return "Erro ao excluir o endereço."


def address_success_create():
    return "Endereço cadastrado com sucesso."


def address_error_create():
    return "Erro ao cadastrar endereço."


def address_success_update():
    return "Endereço atualizado com sucesso."


def address_error_update():
    return "Erro ao atualizar o endereço."


def address_and_person_created():
    return "Dados cadastrados com sucesso."


def address_and_person_not_created():
    return "Erro ao cadastrar os dados."


def recover_database_not_permitted():
    return "Usuário sem permissão de continuar com a operação"


def recover_database_login_incorrect():
    return "O nome de usuário e/ou senha especificados não estão corretos."


def duplicate_cpf(cpf):
    if cpf is not None:
        return "O número de CPF " + cpf + " já existe na base de dados"
    else:
        return "O número de CPF informado já existe na base de dados"


def duplicate_cnpj(cnpj):
    if cnpj is not None:
        return "O número de CNPJ " + cnpj + " já existe na base de dados"
    else:
        return "O número de CNPJ informado já existe na base de dados"
