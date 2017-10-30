// Tratamento de mascaras como cpf e cnpj
$(document).ready(function () {

    if ($('input[mask=cnpj]').length > 0)
        $('input[mask=cnpj]').mask('00.000.000/0000-00', {reverse: true});

    if ($('input[mask=cpf]').length > 0)
        $('input[mask=cpf]').mask('000.000.000-00', {reverse: true});
});
