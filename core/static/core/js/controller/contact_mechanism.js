class ContactMechanism {
	constructor() {
		this._modalOfficeContactMechanism = $('#modal-office-profile-contact-mechanism');
		this._elBtnAddContactMechanism = $('#btn-add-contact-mechanism');
		this.onClickBtnContactMechanism()
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

}