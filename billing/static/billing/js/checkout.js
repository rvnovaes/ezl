class Checkout {
	constructor() {
		this._elModalCheckout = $('#modal-billing-checkout');
		this._elInputName = $('#input-name');		
		this._elInputEmail = $('#input-email');
		this._elInputCPF = $('#input-cpf');
		this._elInputBirth = $('#input-birth');
		this._elInputPhoneNumber = $('#input-phone-number');
		this._elInputBrand = $('[name=input-card-brand]');
		this._elInputCardNumber = $('#input-card-number');
		this._elInputCardExpirationDate = $('#input-card-expiration-date');
		this._elInputCardCVVCode = $('#input-card-cvv-code'); 
		this._elInputZipcode = $('#input-address-zipcode');
		this._elInputStreet = $('#input-address-street');
		this._elInputAddressNumber = $('#input-address-number');
		this._elInputNeighborhood = $('#input-address-neighborhood');
		this._elInputComplement = $('#input-address-complement');
		this._elInputCity = $('#input-address-city');
		this._elState = $('#input-address-state');
		this._elBtnPay = $('#btn-pay');
		this.onClickBtnPay();
		this.onClickBrand();

	}

	get name() {
		return this._elInputCardName.val();
	}

	get email() {
		return this._elInputEmail.val();
	}	

	get cpf() {
		return this._elInputCPF.val();
	}

	get birth() {
		return this._elInputBirth.val();
	}

	get phoneNumber() {
		return this._elInputPhoneNumber.val();
	}

	get cardNumber() {
		return this._elInputCardNumber.val();
	}

	get cardExpirationDate() {
		return this._elInputCardExpirationDate.val();		
	}

	get cardCVVCode() {
		return this._elInputCardCVVCode.val();		
	}	

	openCheckout() {
		this._elModalCheckout.modal('show')
	}

	paymentCallback(error, response) {
		if (error) {
			console.log(error)
		} else {
			console.log(response)
		}
	}

	onClickBrand() {
		$('input[name=btn-brand]').on('click', (evt) => {
			alert();
		})
	}

	onClickBtnPay() {
		this._elBtnPay.on('click', (evt)=> {
			gn_checkout.getPaymentToken({
				brand: 'visa', 
				number: this.cardNumber, 
				cvv: this.cardCVVCode, 
				expiration_month: '05', 
				expiration_year: '2018'
			}, this.paymentCallback)
		})
	}
 }