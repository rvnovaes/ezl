class Register {
    constructor() {
        this.elRegisterForm = $('#register-form');
        this.elEmail = $('input[name=email]');
        this.elPassword = $('input[name=password]');        
        this.elName = $('input[name=name]');
        this.elOfficeCpfCnpj = $('input[name=office_cpf_cnpj]')
        this.elAcceptTerms = $('input[name=accept-terms]'); 
        this.elBtnEye = $('#btn-eye'); 
        this.onSubmit();
        this.onBlurEmail();
        this.onBlurPassword();
        this.onBlurName();
        this.onChangeAcceptTerms();
        this.onClickBtnEye();
        this.onBlurCpfCnpj();
        this.onFocusCpfCnpj();
        this.errors = {'acceptTerms': false};
    }

    get formData() {
        return $("form").serializeArray();
    }    

    get query() {
        let formData = this.formData;
        let data = {};
        $(formData ).each(function(index, obj){
                data[obj.name] = obj.value;
            });     
        return data;
    }

    onBlurCpfCnpj() {
        this.elOfficeCpfCnpj.on('blur', (evt)=>{
            if (this.elOfficeCpfCnpj.val().length <= 11) {
                this.elOfficeCpfCnpj.mask('000.000.000-00', {reverse: true})
            } else {
                this.elOfficeCpfCnpj.mask('00.000.000/0000-00', {reverse: true})
            }
        })
    }

    onFocusCpfCnpj() {
        try {
            this.elOfficeCpfCnpj.on('focus', (evt) => {
                this.elOfficeCpfCnpj.unmask()
            })            
        } catch (error) {
            console.log('Ainda não foi atribuido mascara')
        }

    }

    onSubmit() {
        this.elRegisterForm.on('submit', (el)=>{
            el.preventDefault();            
            if (!Object.keys(this.errors).length) {
                this.save()
            } else {
                this.validateAcceptTerms();
            }            
        })
    }
    onBlurEmail(){
        this.elEmail.on('blur', ()=>{
            delete this.errors['email'];
            this.validateEmail()
        })
    }
    onBlurPassword() {
        this.elPassword.on('blur', ()=>{
            delete this.errors['password'];
            this.validatePassword()
        })        
    }
    onBlurName() {
        this.elName.on('blur', ()=>{
            delete this.errors['name'];
            this.validateName()
        })        
    }        
    onChangeAcceptTerms() {
        this.elAcceptTerms.on('change', ()=>{
            this.validateAcceptTerms();
        })
    }
    onClickBtnEye() {
        this.elBtnEye.on('click', ()=>{
            if (this.elPassword.attr('type') == 'password') {
                this.elPassword.attr('type', 'text')                
                this.elBtnEye.children('i').attr('class', 'fa fa-eye-slash')
            } else {
                this.elPassword.attr('type', 'password')
                this.elBtnEye.children('i').attr('class', 'fa fa-eye')
            }
        })
    }
    validateEmail() {
        $.ajax({
            method: 'POST', 
            url: '/validate_email/',
            data: this.query, 
            success: (response) => {                
                if (!response.valid) {
                    this.errors['email'] = false;
                    this.elEmail.closest('.form-group').addClass('has-error');
                    this.elEmail.siblings().css('display', 'block');

                } else {
                    this.elEmail.closest('.form-group').removeClass('has-error');
                    this.elEmail.siblings().css('display', 'none');
                }
            }, 
            error: (error) => {
                console.log(error)
            },
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
            },
            dataType: 'json'            
        })       

    }
    validatePassword() {
        $.ajax({
            method: 'POST', 
            url: '/validate_password/',
            data: this.query, 
            success: (response) => {                
                console.log(response)
                $('#password-error').empty()
                if (!response.valid) {                    
                    this.elPassword.closest('.form-group').addClass('has-error');
                    $('#password-error').css('display', 'block');
                    response.message.forEach((message)=>{
                        $('#password-error').append('* ' + message);
                    })                    

                } else {
                    this.elPassword.closest('.form-group').removeClass('has-error');
                    $('#password-error').css('display', 'none');
                }
            }, 
            error: (error) => {
                console.log(error)
            },
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
            },
            dataType: 'json'            
        })               
    }
    validateName() {
        if (this.elName.val().trim().split(' ').length <= 1) {
            this.errors['name'] = false;
            this.elName.closest('.form-group').addClass('has-error')
            this.elName.siblings().css('display', 'block');
        } else {
            this.elName.closest('.form-group').removeClass('has-error')            
            this.elName.siblings().css('display', 'none');
        }
    }
    validateCpfCnpj() {
        
    }
    validateAcceptTerms() {
        if (this.elAcceptTerms.is(':checked')) {
            delete this.errors['acceptTerms'];
            this.elAcceptTerms.closest('.form-group').removeClass('has-error')            
            this.elAcceptTerms.siblings('span').css('display', 'none');            
        } else {
            this.errors['acceptTerms'] = false;
            this.elAcceptTerms.closest('.form-group').addClass('has-error')
            this.elAcceptTerms.siblings('span').css('display', 'block');            
        }                        
    }    
    save() {
        swal({
            title: 'Criando seu escritório', 
            text: 'Aguarde um momento',
            onOpen: ()=>{
                swal.showLoading()
                $.ajax({
                    method: 'POST', 
                    data: this.query, 
                    success: (response) => {                
                        window.location.href = response.redirect                                
                        swal.close();
                    }, 
                    error: (error) => {
                        console.log(error)
                    },
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
                    },
                    dataType: 'json'            
                })                
            }
        })       
    }

}