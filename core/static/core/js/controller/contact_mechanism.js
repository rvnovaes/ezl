class ContactMechanism {
	constructor() {
		this._modalOfficeContactMechanism = $('#modal-office-profile-contact-mechanism');
		this._elBtnAddContactMechanism = $('#btn-add-contact-mechanism');
		this._elBtnDeleteContactMechanism = $('#btn-delete-contact-mechanism');
		this.contactMechanismSelected = [];
		this.onClickBtnContactMechanism();
		this.onSubmitForm();
		this.onCheckItem();
		this.onClickBtnDeleteContactMechanism();
	}

	get form() {
		return $("#form-contact-mechanism")
	}	

	onClickBtnContactMechanism(){
		this._elBtnAddContactMechanism.on('click', ()=> {
			this.showOfficeContactMechanismForm();
		})
	}

	showOfficeContactMechanismForm() {
		this._modalOfficeContactMechanism.modal('show');
	};	    

	hideOfficeContactMechanismForm() {
		this._modalOfficeContactMechanism.modal('hide');
	};	

	onSubmitForm() {
		this.form.on('submit', (event)=>{			
			swal({
				title: 'Aguarde',
				onOpen() {
					swal.showLoading();
				}
			})
		})
	}

	onClickBtnDeleteContactMechanism() {
		this._elBtnDeleteContactMechanism.on('click', ()=>{
			this.deleteContactMechanism();
		})
	}

	onCheckItem(){
		let self = this;
        $('#contact-mechanism-table input:checkbox').on('change', function(){
            if ($(this).is(':checked')) {
                self.contactMechanismSelected.push($(this).val())    
            } else {
                self.contactMechanismSelected.splice(self.contactMechanismSelected.indexOf($(this).val(), 1))
            }                            
        })		
	}			

	deleteContactMechanism() {
		swal({
		  title: 'Esta operação é irreversível',
		  text: "Deseja realmente deletar!",
		  type: 'warning',
		  showCancelButton: true,
		  confirmButtonColor: '#3085d6',
		  cancelButtonColor: '#d33',
		  confirmButtonText: 'Sim, quero deletar!'
		}).then((result) => {
		  if (result.value) {
	  		$.ajax({
	  			method: 'POST',
	  			url: '/office_profile_contact_mechanism_delete/', 
	  			data: {ids: this.contactMechanismSelected}, 
	            success: function (response) {
				    swal({
					      title: 'Contatos deletados com sucesso!',				      
					      type: 'success'				    	
				    	}
				    )	                
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