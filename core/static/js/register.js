class Register {
    constructor() {
        this.elRegisterForm = $('#register-form');        
        this.onSubmit();
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
            this.save()
        })
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