new_success = "Registro Criado com Sucesso"
update_success = "Registro Atualizado com Sucesso"


def delete_success(model_name):
    return "Registros selecionados de " + model_name + " excluídos com sucesso"


def delete_error_protected(model_name, related_model):
    return "Não é possível excluir o(s) registros de " + model_name + " porque existem registros " \
                                                                      "associados em outra parte do sistema!" \
                                                                      " A exclusão será cancelada."
