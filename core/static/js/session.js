/*
Este cara e responsavel por atualizar e buscar a sessao customizada do usuario.
Ex: O Escritorio que usuario esta trabalhando
*/

$(document).ready(function(){
    $('#current_office').text('...');
    $.ajax({
        type: 'GET',
        url: '/session/',
        data: {},
        success: function(response) {
            console.log(response);
            localStorage.setItem('custom_session_user', response);
            if (response.current_office_name){                
                $('#current_office').text(response.current_office_name);
            } else {
                $('#current_office').text('Nenhum escritório selecionado');
            }
        }
    })
});

var updateSession = function(key, value, csrf_token){
    var data = {}
    data[key] = value
    $.ajax({
        type: 'POST',
        url: '/session/',
        data: data,
        success: function(response){
                if (response.current_office_name) {
                    var current_office_name = response.current_office_name;
                    var current_office_pk = response.current_office_pk;
                    $('#current_office').text(response.current_office_name);
                    localStorage.setItem
                }else{
                    $('#current_office').text('Todos');
                    localStorage.clear();
                }
                if (response.modified){
                    location.href = '/';
                }
            },
        beforeSend: function(xhr, settings){
            xhr.setRequestHeader('X-CSRFToken', csrf_token)
        }
    })
};
