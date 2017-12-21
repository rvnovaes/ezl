function logout(scriptSrc) {
    //Verifica se o script que gera conflito com o modal foi carregado, caso tenha sido, aciona o jQuery.noConflict()
    var len = $('script').filter(function () {
        return ($(this).attr('src') == scriptSrc);
    }).length;
    if(len > 0){
        jQuery.noConflict();
        $('#logout_modal').modal('show');
    }else{
        $('#logout_modal').modal('show');
    }
}