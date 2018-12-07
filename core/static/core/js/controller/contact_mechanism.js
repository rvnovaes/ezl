class ContactMechanism {
	constructor() {
		this._modalOfficeContactMechanism = $('#modal-office-profile-contact-mechanism');
		this._elBtnAddContactMechanism = $('#btn-add-contact-mechanism');
		this.onClickBtnContactMechanism();
		this.onSubmitForm();
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

}