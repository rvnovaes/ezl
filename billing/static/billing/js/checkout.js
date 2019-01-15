class Checkout {
	constructor(csrfToken, chargeId, callbackToPay) {		
		this.csrfToken = csrfToken;
		this.chargeId = chargeId;
		this.billingDetails = null;
		this._elModalCheckout = $('#modal-billing-checkout');
		this._elInputName = $('#input-name');		
		this._elInputEmail = $('#input-email');
		this._elInputCPF = $('#input-cpf').mask('000.000.000-00', {reverse: true});
		this._elInputBirth = $('#input-birth');
		this._elInputPhoneNumber = $('#input-phone-number').mask('(00) 00000-0000');
		this._elBrand = $('.brand');
		this._elInputCardNumber = $('#input-card-number');
		this._elInputCardExpirationDate = $('#input-card-expiration-date').mask('00/0000');
		this._elInputCardCVVCode = $('#input-card-cvv-code').mask('0000'); 
		this._elInputZipcode = $('#input-address-zipcode').mask('00000-000');
		this._elInputStreet = $('#input-address-street');
		this._elInputAddressNumber = $('#input-address-number');
		this._elInputNeighborhood = $('#input-address-neighborhood');
		this._elInputComplement = $('#input-address-complement');
		this._elInputCity = $('#input-address-city');
		this._elState = $('#input-address-state');
		this._elBtnPay = $('#btn-pay');
		this._elPaymentPending = $('#payment-pending');
		this._elInputUseBillingDetails = $('[name=use-billing-details]');
		this._panelPersonalData = $('#panel-personal-data');
		this._panelBillingAddress = $('#panel-billing-address');
		this.cards = {
			visa: /^4\d+$/,
			mastercard: /^5\d+$/, 
			elo: /^(636368|438935|504175|451416|636297|509049|509069|509050|509074|509068|509040|509045|509051|509046|509066|509047|509042|509052|509043|509064|509040|36297|5067|4576|4011)/,
			amex: /^(34|37)/, 
			diners: /^(30|36|38)/,
			discover: /^(6011|622|64|65)/, 
			jcb: /^35/, 
		};
		this.onClickBtnPay();		
		this.onChangeZipcode();		
		this.onKeyUpCardNumber();
		this.onDocumentReady();
	}

	get name() {
		return this._elInputName.val();
	}

	set name(value) {
		this._elInputName.val(value);
	}

	get email() {
		return this._elInputEmail.val();
	}

	set email(value) {
		this._elInputEmail.val(value);
	}

	get cpf() {
		return this._elInputCPF.cleanVal();
	}

	set cpf(value) {
		this._elInputCPF.val(value);
	}

	get birth() {
		return this._elInputBirth.val();
	}

	set birth(value) {
		this._elInputBirth.val(value);
	}

	get phoneNumber() {
		return this._elInputPhoneNumber.cleanVal();
	}

	set phoneNumber(value) {
		this._elInputPhoneNumber.val(value);
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
		return this._elInputZipcode.cleanVal();
	}

	set zipcode(value) {
		this._elInputZipcode.val(value);
	}

	get street() {
		return this._elInputStreet.val();
	}

	set street(value) {
		this._elInputStreet.val(value);
	}

	get addressNumber() {
		return this._elInputAddressNumber.val();
	}

	set addressNumber(value) {
		this._elInputAddressNumber.val(value);
	}

	get neighborhood() {
		return this._elInputNeighborhood.val();
	}

	set neighborhood(value) {
		this._elInputNeighborhood.val(value);
	}

	get addressComplement() {
		return this._elInputComplement.val();
	}

	set addressComplement(value) {
		this._elInputComplement.val(value);
	}

	get city() {
		return this._elInputCity.val();
	}

	set city(value) {
		this._elInputCity.val(value);
	}

	get state() {
		return this._elState.val();
	}

	set state(value) {
		this._elState.val(value);
	}

	checkUseBillingDetails() {
		this._elInputUseBillingDetails.prop('checked', true);
	}

	uncheckUseBillingDetails() {
		this._elInputUseBillingDetails.prop('checked', false);
	}

	hidePersonalData(){
		this._panelPersonalData.find('.panel-wrapper').collapse('hide');
	}

	showPersonalData(){
		this._panelPersonalData.find('.panel-wrapper').collapse('show');
	}

	hideBillingAddress(){
		this._panelBillingAddress.find('.panel-wrapper').collapse('hide');
	}

	showBillingAddress(){
		this._panelBillingAddress.find('.panel-wrapper').collapse('show');
	}

	onKeyUpCardNumber() {
		this._elInputCardNumber.on('keyup', (evt)=> {
			$('.brand').css("filter", "grayscale(100%)");
			Object.keys(this.cards).forEach((key) => {
				if (this.cards[key].test(this.cardNumber)) {					
					this.cardBrand = key;					
				}
			});
			$(`[brand=${this.cardBrand.toUpperCase()}]`).css("filter", "grayscale(0)");
		});
	}

	openCheckout(chargeId) {
		this.chargeId = chargeId;
		this._elModalCheckout.modal('show');
		this.fillBillingDetails();
	}

	paymentCallback(error, response, options) {
		if (error) {
			console.log(error);
			swal.close();
			swal({
				title: 'Atenção!',
				text : error, 
				type: error.error_description,
				confirmButtonText: 'ok'
			});
		} else {
			console.log(response);
			confirmPayment(chargeId, response.data.payment_token, dataPayment, csrfToken);
		}
	}

	checkStatus() {	
		let chargeId = this.chargeId;		
		if (!chargeId) {
			chargeId = gnData.charge_id;			
		}		
		$.ajax({
				url: `/billing/detail_payment/${chargeId}`, 
				method: 'GET', 
				dataType: 'json', 
				success: (response)=> {
					gnData = response.data;
					if (response.data.status === 'paid') {
						taskDetail.servicePriceTableId = response.data.custom_id;
						taskDetail.setServicePriceDetail(response.data.custom_id);
						taskDetail.delegateTaskPaid(gnData, this.intervalCheckStatus);

					} else  {						
						if (response.data.status === 'waiting') {
							taskDetail.billing.checkout.showPaymentPending();
						} 						
					}
				}
			});
		}	

	getPaymentStatus() {									
		window.scroll(0, 0);
		this.checkStatus();
		this.intervalCheckStatus = setInterval(this.checkStatus, 10000);
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
				console.log(response);
			},
			error: (error) => {

			}, 
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", self.csrfToken)
			}, 
		});
	} 

	onChangeZipcode() {
		this._elInputZipcode.on('change', (evt)=> {
			$.ajax({
				method: 'GET',
				url: `https://viacep.com.br/ws/${this.zipcode}/json/unicode/`, 
				success: (response)=>{
					this.street = response.logradouro;
					this.neighborhood = response.bairro;
					this.city = response.localidade;
					this.addressComplement = response.complemento;
					this.state = response.uf;
				}
			});
		});
	}

	validateForm() {
		let formValid = true
		$('#form-checkout').find('input').each(function(el) {
			if ($(this).prop('required') && $(this).val().length === 0) {
				$(this).parent().addClass('has-error');
				formValid = false;
			}
		});
		return formValid;
	}

	onClickBtnPay() {
		$('#form-checkout').submit(function (e) {
            e.preventDefault();
        });		
		this._elBtnPay.on('click', (evt)=> {
			if (this.validateForm()) {
				swal({
					title: 'Processando pagamento', 
					text: 'Aguarde...',
					onOpen: ()=>{
						swal.showLoading();
					}
				});
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
				chargeId = this.chargeId;
				confirmPayment = this.confirmPayment;
				if (this.validateForm()){
					this.getPaymentStatus();
					gn_checkout.getPaymentToken({
						brand: this.cardBrand.toLowerCase(), 
						number: this.cardNumber, 
						cvv: this.cardCVVCode, 
						expiration_month: this.cardExpirationDate.slice(0,2), 
						expiration_year: this.cardExpirationDate.slice(3,7)
					}, this.paymentCallback)
				}
			}			
		});
	}

    showPaymentPending() {
        this._elPaymentPending.css('display', 'block');
        $('[data-target]').css('display', 'none');
    }

    hidePaymentPending() {
        this._elPaymentPending.css('display', 'none');
    }

    setBillingDetails() {
		$.ajax({
			method: 'GET',
			url: `/billing/get_office_billing_detail/`,
			success: (response)=>{
				if (response.id){
					this.billingDetails = response;
				}
			}
		});
	}

	fillBillingDetails() {
		if(this.billingDetails){
			this.checkUseBillingDetails();
			this.name = this.billingDetails.card_name;
			this.email = this.billingDetails.email;
			this.cpf = this.billingDetails.cpf_cnpj;
			this.birth = this.billingDetails.birth_date;
			this.phoneNumber = this.billingDetails.phone_number;
			this.zipcode = this.billingDetails.billing_address.zip_code;
			this.street = this.billingDetails.billing_address.street;
			this.addressNumber = this.billingDetails.billing_address.number;
			this.neighborhood = this.billingDetails.billing_address.city_region;
			this.addressComplement = this.billingDetails.billing_address.complement;
			this.city = this.billingDetails.billing_address.city_name;
			this.state = this.billingDetails.billing_address.state_name;
			this.hidePersonalData();
			this.hideBillingAddress();
		}else{
			this.uncheckUseBillingDetails();
			this.showPersonalData();
			this.showBillingAddress();
		}
	}

    onDocumentReady(){
	    $(document).ready(()=>{
			this.setBillingDetails();
        });
    }
  
 }

var dataPayment;
var csrfToken;
var chargeId;
var confirmPayment;
var gnData;