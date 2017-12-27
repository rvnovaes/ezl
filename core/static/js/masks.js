// Tratamento de mascaras como cpf e cnpj
function loadInputsMask(){
    if ($('input[mask=cnpj]').length > 0)
        $('input[mask=cnpj]').mask('00.000.000/0000-00', {reverse: true});

    if ($('input[mask=cpf]').length > 0)
        $('input[mask=cpf]').mask('000.000.000-00', {reverse: true});

    if ($('input[mask=money]').length > 0)
        $('input[mask=money]').maskMoney({thousands: ".", decimal: ",", allowZero: true});
}

$(document).ready(function () {
    loadInputsMask();
});
