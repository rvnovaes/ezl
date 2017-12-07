// Tratamento de mascaras como cpf e cnpj
function loadInputsMask(){
    $('input[mask=cnpj]').mask('00.000.000/0000-00', {reverse: true});
    $('input[mask=cpf]').mask('000.000.000-00', {reverse: true});
    $('input[mask=money]').maskMoney({thousands: ".", decimal: ",", allowZero: true});
}

$(document).ready(function () {
    loadInputsMask();
});
