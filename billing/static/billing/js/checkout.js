class Checkout {
	constructor() {
		this._elModalCheckout = $('#modal-billing-checkout');
		this._elInputCardNumber = $('#input-card-number');
		this._elInputCardExpirationDate = $('#input-card-expiration-date');
		this._elInputCardCVVCode = $('#input-card-cvv-code'); 
		this._elInputCardName = $('#input-card-name');		
		this._elBtnPay = $('#btn-pay');
		this.onClickBtnPay();
		this.onClickBrand();

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

	get cardName() {
		return this._elInputCardName.val();
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