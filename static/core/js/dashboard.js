// Esta funcionalida foi implementada para que ao clicar em ordenar ou paginar as tabelas nao sejam fechadas
// Isso ocorre pelo fato de ao clicar em ordenar ou paginar, uma nova requisicao e realizada para o servidor
// E uma nova pagina e retornada
// Para resolver este problema a ultima requisicao clicada e armazenada no sessionStorage

$(document).ready(function () {
    var div_states = ['.RETURN', '.ACCEPTED', '.OPEN', '.DONE', '.REFUSED', '.BLOCKEDPAYMENT', '.FINISHED'];
    div_states.forEach(function (state) {
        $(state).on('click', function () {
            sessionStorage.setItem('dashboard-state-on', state);
        });
    });

    var state_class = sessionStorage.getItem('dashboard-state-on');
    if (state_class){
        var state_id = state_class.replace('.', '#');
        $(state_id).removeAttr('class', 'collapse');
    }
});