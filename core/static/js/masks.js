// Tratamento de mascaras como cpf e cnpj
$(document).ready(function () {
    $('input[mask=cnpj]').mask('00.000.000/0000-00', {reverse: true});
    $('input[mask=cpf]').mask('000.000.000-00', {reverse: true});
});