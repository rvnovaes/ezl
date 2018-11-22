class Register {
    constructor() {
        this.elRegisterForm = $('#register-form');
        this.elEmail = $('input[name=email]');
        this.elPassword = $('input[name=password]');        
        this.elName = $('input[name=name]');
        this.elAcceptTerms = $('input[name=accept-terms]')
        this.onSubmit();
        this.onBlurEmail();
        this.onBlurPassword();
        this.onBlurName();
        this.onChangeAcceptTerms();
        this.errors = {};
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
                this.elPassword.siblings().empty()
                if (!response.valid) {                    
                    this.elPassword.closest('.form-group').addClass('has-error');
                    this.elPassword.siblings().css('display', 'block');
                    response.message.forEach((message)=>{
                        this.elPassword.siblings().append('* ' + message);
                    })                    

                } else {
                    this.elPassword.closest('.form-group').removeClass('has-error');
                    this.elPassword.siblings().css('display', 'none');
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
        $.ajax({
            method: 'POST', 
            data: this.query, 
            success: (response) => {                
                window.location.href = response.redirect                                
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

}