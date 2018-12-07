class Address {
	constructor() {
		this._modalOfficeAddress = $('#modal-office-profile-address');
		this._elBtnAddAddress = $('#btn-add-address');
		this.onClickBtnAddress();
		this.onSubmitForm();
	}

	get form() {
		return $("#form-address")
	}	

	onClickBtnAddress(){
		this._elBtnAddAddress.on('click', ()=> {
			this.showOfficeAddressForm();
		})
	}

	showOfficeAddressForm() {
		this._modalOfficeAddress.modal('show');
	};	    

	hideOfficeAddressForm() {
		this._modalOfficeAddress.modal('hide');
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