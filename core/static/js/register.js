class Register {
    constructor() {
        this.elRegisterForm = $('#register-form');
        this.elEmail = $('input[name=email]');
        this.elPassword = $('input[name=password]');        
        this.elName = $('input[name=name]');
        this.elOfficeCpfCnpj = $('input[name=cpf_cnpj]')
        this.elAcceptTerms = $('input[name=accept-terms]'); 
        this.elBtnEye = $('#btn-eye'); 
        this.officeExist;
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

    onFocusCpfCnpj() {
        try {
            this.elOfficeCpfCnpj.on('focus', (evt) => {
                this.elOfficeCpfCnpj.unmask()
            })            
        } catch (error) {
            console.log('Ainda não foi atribuido mascara')
        }

    }

    requestInvitation() {
        swal({
            title: 'Atenção!',
            type: 'warning',
            text: `
                O escritório/empresa ${this.officeExist.legal_name} com esse CPF/CNPJ já existe. 
                Deseja enviar uma solicitação de ingresso para este escritório/empresa?
            `, 
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            cancelButtonText: 'Não', 
            confirmButtonText: 'Sim', 
            reverseButtons: true             
        }).then((result => {
            if (result.value) {
                this.save(true);
            }
        }))
    }


    onSubmit() {
        this.elRegisterForm.on('submit', (el)=>{
            el.preventDefault();
            if (this.officeExist.exist) {
                this.requestInvitation();
            } else {
                if (!Object.keys(this.errors).length) {
                    this.save()
                } else {
                    this.validateAcceptTerms();
                }
            }                     
        })
    }
    onBlurCpfCnpj() {
        this.elOfficeCpfCnpj.on('blur', (evt)=>{
            delete this.errors['email'];
            this.validateCpfCnpj();
            this.checkOfficeExist();
            if (this.elOfficeCpfCnpj.val().length <= 11) {
                this.elOfficeCpfCnpj.mask('000.000.000-00', {reverse: true})
            } else {
                this.elOfficeCpfCnpj.mask('00.000.000/0000-00', {reverse: true})
            }; 
        })
    }    
    onBlurEmail(){
        this.elEmail.on('blur', ()=>{
            delete this.errors['email'];
            this.validateEmail();
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
    addClassError(el, siblingsParam) {
        el.closest('.form-group').addClass('has-error')
        if (siblingsParam) {
            el.siblings(siblingsParam).css('display', 'block');
        } else {
            el.siblings().css('display', 'block');
        }        
    }
    removeClassError(el, siblingsParam) {
        el.closest('.form-group').removeClass('has-error');
        if (siblingsParam) {
            el.siblings(siblingsParam).css('display', 'none');
        } else {
            el.siblings().css('display', 'none');
        }                
    }

    validateCpfCnpj() {
        $.ajax({
            method: 'POST', 
            url: '/validate_cpf_cnpj/', 
            data: this.query, 
            success: (response) => {
                if (!response.valid) {
                    this.errors['cpf_cnpj'] = false;
                    this.addClassError(this.elOfficeCpfCnpj);                    
                } else {
                    this.removeClassError(this.elOfficeCpfCnpj)
                }
            }
        })
    }
    checkOfficeExist() {
        let query = this.query;
        query['model'] = 'office'
        $.ajax({
            method: 'POST', 
            url: '/check_cpf_cnpj_exist', 
            data: query, 
            success: (response) => this.officeExist = response
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
                    this.addClassError(this.elEmail);                  
                } else {
                    this.removeClassError(this.elEmail);
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
            this.addClassError(this.elName)
        } else {
            this.removeClassError(this.elName)
        }
    }
    validateAcceptTerms() {
        if (this.elAcceptTerms.is(':checked')) {
            delete this.errors['acceptTerms'];
            this.removeClassError(this.elAcceptTerms, 'span');            
        } else {
            this.errors['acceptTerms'] = false;
            this.addClassError(this.elAcceptTerms, 'span');            
        }                        
    }    
    save(requestInvite) {
        swal({
            title: 'Criando seu escritório', 
            text: 'Aguarde um momento',
            onOpen: ()=>{
                swal.showLoading()
                let query = this.query;
                query['request_invite'] = requestInvite
                if (requestInvite) {
                    query['office_pk'] = this.officeExist.id
                }
                $.ajax({
                    method: 'POST', 
                    data: query, 
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