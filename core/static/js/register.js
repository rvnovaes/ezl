(function() {
    wizard = $('#registerForm').wizard({
        buttonLabels: {
            next: 'Próximo',
            back: 'Anterior',
            finish: 'Finalizar'
        },
        onInit: function() {
            $('#validation').formValidation({
                framework: 'bootstrap',
                fields: {
                    name: {
                        validators: {
                            notEmpty: {
                                message: 'O campo de nome é obrigatório'
                            }
                        }
                    },
                    username: {
                        validators: {
                            notEmpty: {
                                message: 'O nome de usuário é obrigatório'
                            },
                            remote: {
                                message: 'Este usuário já existe na nossa base de dados',
                                url: '/validate_username/',
                                type: 'POST',
                                delay: 1000,
                                data: function(validator, $field, value) {
                                    return {
                                        csrfmiddlewaretoken: validator.getFieldElements('csrfmiddlewaretoken').val()
                                    };
                                }
                            },
                        }
                    },
                    email: {
                        validators: {
                            notEmpty: {
                                message: 'O e-mail é obrigatório'
                            },
                            emailAddress: {
                                message: 'O valor inserido não é um endereço de e-mail válido'
                            },
                            remote: {
                                message: 'Já existe um usuário cadastrado com este e-mail',
                                url: '/validate_email/',
                                type: 'POST',
                                delay: 1000,
                                data: function(validator, $field, value) {
                                    return {
                                        csrfmiddlewaretoken: validator.getFieldElements('csrfmiddlewaretoken').val()
                                    };
                                }
                            },
                        }
                    },
                    password: {
                        threshold: 8,
                        validators: {
                            notEmpty: {
                                message: 'É obrigatório uma senha de acesso'
                            },
                            different: {
                                field: 'username',
                                message: 'A senha não pode ser a mesma do usuário'
                            },
                            remote: {
                                message: 'A senha não atende aos requisitos',
                                url: '/validate_password/',
                                type: 'POST',
                                data: function(validator, $field, value) {
                                    return {
                                        csrfmiddlewaretoken: validator.getFieldElements('csrfmiddlewaretoken').val()
                                    };
                                }
                            }
                        }
                    },
                    confirmpassword: {
                        validators: {
                            identical: {
                                field: 'password',
                                message: 'Os valores digitados para os campos de senha não conferem'
                            }
                        }
                    },
                    legal_name: {
                        validators: {
                            callback: {
                                message: 'Este campo é obrigatório',
                                callback: function (value, validator, $field) {
                                    var select_office_register = $('input[name=select_office_register]').val();
                                    if (select_office_register === '2'){
                                        return value !== '';
                                    }else{
                                        return true;
                                    }
                                }
                            },
                        }
                    },
                    filter_office_legal_name: {
                        validators: {
                            callback: {
                                message: "Favor selecionar pelo menos um escritório para se vincular",
                                callback: function (value, validator, $field) {
                                    var select_office_register = $('input[name=select_office_register]').val();
                                    if (select_office_register === '1'){
                                        retorno = false
                                        $('input[id^=office_checkbox_]').each(function (index) {
                                            if ($( this ).prop("checked")){
                                                retorno = true;
                                            }
                                        });
                                        return retorno;
                                    }else{
                                        return true;
                                    }
                                }
                            }
                        }
                    }
                }
            });
        },
        validator: function() {
            var fv = $('#validation').data('formValidation');
            var $this = $(this);
            var current_tab = wizard._current
            // Validate the container
            fv.validateContainer($this);
            var isValidStep = fv.isValidContainer($this);
            if (isValidStep === false || isValidStep === null) {
                return false;
            }else if (hidden_field_validation(current_tab) == false){
                $('#tab-'+ wizard._current +'-alert').show();
                return false;
            }else if (current_tab == '3' && !$("#terms").prop('checked')){
                $('label[for=terms]').addClass('text-danger')
                return false
            }
            $('#tab-'+ current_tab +'-alert').hide();
            $('label[for=terms]').removeClass('text-danger')
            return true;
        },
        onAfterChange: function(from, to) {
            var select_office_register = $('input[name=select_office_register]').val();
            if(select_office_register === "1" && to.index === 2) {
                if (from.index === 1) {
                    $('#registerForm').wizard('next');
                }
                else if (from.index === 3) {
                    $('#registerForm').wizard('back');
                }
            }
        },
        onFinish: function() {
            $('#validation')[0].submit();
        },
    }).data('wizard');
    function hidden_field_validation(currentIndex){
        retorno = false;
        var select_office_register = $('input[name=select_office_register]').val();
        switch (currentIndex) {
            case 1:
                if (select_office_register !== ""){retorno = true}
                break;
            case 2:
                if (select_office_register !== "1") {
                    $('input[id*=radio]').each(function () {
                        if ($(this).prop('checked')) {
                            retorno = true;
                        }
                    });
                } else {retorno = true}
                break;
            default:
                retorno = true;
                break;
        }
        return retorno
    }
    wizard.get('#plan_tab').setLoader(function () {
        var select_office_register = $('input[name=select_office_register]').val();
        if (select_office_register === '1'){
            return '<strong>Você está inscrito nos planos contratados pelos escritórios aos quais deseja se vincular</strong>';
        }else{
            return $('#plan_tab').html();
        }
    });
    wizard.get('#confirm_tab').setLoader(function() {
        var name = $('input[name=name]').val();
        var username = $('input[name=username]').val();
        var email = $('input[name=email]').val();
        var select_office_register = $('input[name=select_office_register]').val();
        var plan_name = sessionStorage.getItem('plan_name');
        var plan_month_value = sessionStorage.getItem('plan_month_value');
        $('#name').html(name);
        $('#username').html(username);
        $('#email').html(email);
        $('div[id^=select_office_register-]').addClass('hidden')
        $('#select_office_register-'+select_office_register).removeClass('hidden')
        $('#selected-plan').html('')
        switch (select_office_register) {
            case '1':
                $('#office_list').html('')
                $('.card-fixed').each(function (index) {
                    office_legal_name = $( this ).find("span.office-legal-name small").html();
                    office_city = $( this ).find("span#office-city").html();
                    (office_city) ? office_city = ' - ' + office_city : office_city = '';
                    $('#office_list').append(office_legal_name + office_city + '<br />')
                });
                $('#selected-plan').append('<strong>Você está inscrito nos planos contratados pelos escritórios aos quais deseja se vincular</strong>')
                break;
            case '2':
                var legal_name = $('input[name=legal_name]').val();
                var office_name = $('input[name=office_name]').val();
                var legal_type = $('select[name=legal_type]').find(":selected").text();
                var cpf_cnpj = $('input[name=cpf_cnpj]').val();
                $('#legal_name').html(legal_name);
                $('#office_name').html(office_name);
                $('#legal_type').html(legal_type);
                $('#cpf_cnpj').html(cpf_cnpj);
                $('#selected-plan_name').append(plan_name);
                $('#selected-plan_month_value').append(plan_month_value);
                break;
            case '3':
                $('#selected-plan_name').append(plan_name);
                $('#selected-plan_month_value').append(plan_month_value);
                break;
        }
        return $('#confirm_tab').html()
      });
})();

$("#select_office_register div a").on('click', function () {
    $('.select_office_list').removeClass("selected");
    $(this).addClass("selected");
    $('input[name=select_office_register]').val($(this).data('id'));
    $('div[id^="select_office_detail_"]').addClass("hide");
    $("#select_office_detail_"+$(this).data('id')).removeClass("hide");
});

function select_office(office_id) {
    var office_input = $('#office_checkbox_'+office_id);
    var office_icon = $('#icon-'+office_id);
    var office_title = $('#title-'+office_id);
    var button_action = $('#button_action-'+office_id);
    var office_card = $('#office-'+office_id);
    office_input.trigger('click');
    addOrRemove = office_input.prop("checked");
    office_icon.toggleClass('fa-check', !addOrRemove);
    office_icon.toggleClass('fa-times', addOrRemove);
    button_action.toggleClass('btn-custom', !addOrRemove);
    button_action.toggleClass('btn-danger', addOrRemove);
    button_action.toggleClass('card-fixed', addOrRemove);
    office_title.html(' Remover') ? addOrRemove : office_title.html(' Selecionar');
    $('#validation').formValidation('revalidateField', 'filter_office_legal_name');
}
function choose_plan(plan_button) {
    var radio_select = plan_button.dataset['select'];
    var radio_value = plan_button.dataset['value'];
    var plan_name = plan_button.dataset['name'];
    var plan_month_value = plan_button.dataset['month_value'];
    var radio_field = $('input[name='+radio_select+'][value='+radio_value+']');
    var plan_div = $('#'+radio_select+'-'+radio_value+'-box');
    var field_state = radio_field.prop('checked');
    radio_field.prop('checked', !field_state);
    $('div[id*=box]').removeClass('featured-plan');
    sessionStorage.setItem('plan_name', plan_name);
    sessionStorage.setItem('plan_month_value', plan_month_value);
    if(!field_state){plan_div.addClass('featured-plan');}
}