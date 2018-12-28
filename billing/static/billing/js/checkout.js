class Checkout {
	constructor(csrfToken) {
		this.csrfToken = csrfToken;
		this.charge_id;
		this._elModalCheckout = $('#modal-billing-checkout');
		this._elInputName = $('#input-name');		
		this._elInputEmail = $('#input-email');
		this._elInputCPF = $('#input-cpf');
		this._elInputBirth = $('#input-birth');
		this._elInputPhoneNumber = $('#input-phone-number');
		this._elBrand = $('.brand');
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
		return this._elInputName.val();
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

	get zipcode() {
		return this._elInputZipcode.val();
	}	

	get street() {
		return this._elInputStreet.val();
	}

	get addressNumber() {
		return this._elInputAddressNumber.val();
	}

	get neighborhood() {
		return this._elInputNeighborhood.val();
	}

	get addressComplement() {
		return this._elInputComplement.val();
	}

	get city() {
		return this._elInputCity.val();
	}

	get state() {
		return this._elState.val();
	}

	openCheckout(charge_id) {
		this.charge_id = charge_id
		this._elModalCheckout.modal('show')
	}

	paymentCallback(error, response, options) {
		if (error) {
			console.log(error)
		} else {
			console.log(response)
			confirmPayment(chargeId, response.data.payment_token, dataPayment, csrfToken)
		}
	}

	confirmPayment(chargeId, paymentToken, data, csrfToken) {
		data['charge_id'] = chargeId;
		data['payment_token'] = paymentToken;
		$.ajax({
			url: '/billing/confirm_payment/', 
			method: 'POST', 			
		    contentType: 'application/json; charset=utf-8',	
			dataType: 'json',
			data: JSON.stringify(data), 
			success: (response) => {				
				$('#task_detail').unbind('submit').submit();
			},
			error: (error) => {

			}, 
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", self.csrfToken)
			}, 
		})
	} 

	onClickBrand() {
		this._elBrand.on('click', (evt) => {
			this.cardBrand = $(evt.toElement).attr('brand');
			$('.brand').css("filter", "grayscale(100%)")
			$(evt.toElement).css("filter", "grayscale(0)")
		})
	}

	onClickBtnPay() {
		this._elBtnPay.on('click', (evt)=> {
			swal({
				title: 'Processando', 
				onOpen: ()=>{
					swal.showLoading();
				}
			})
			dataPayment = {
				data: {
					installments: 1, 				 
					billing_address: {
						street: this.street, 
						number: this.addressNumber, 
						neighborhood: this.neighborhood, 
						zipcode: this.zipcode, 
						city: this.city, 
						state: this.state
					}, 
					customer: {
						name: this.name, 
						email: this.email, 
						cpf: this.cpf, 
						birth: this.birth, 
						phone_number: this.phoneNumber, 				
					}				
				}
			};			
			csrfToken = this.csrfToken;
			chargeId = this.charge_id;
			confirmPayment = this.confirmPayment;
			gn_checkout.getPaymentToken({
				brand: this.cardBrand.toLowerCase(), 
				number: this.cardNumber, 
				cvv: this.cardCVVCode, 
				expiration_month: this.cardExpirationDate.slice(0,2), 
				expiration_year: this.cardExpirationDate.slice(3,7)
			}, this.paymentCallback)
		})
	}
 }

var dataPayment;
var csrfToken;
var chargeId;
var confirmPayment;