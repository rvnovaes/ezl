class Billing {
	constructor(lightbox) {
		this.lightbox=lightbox;
		this.payments_forms = ['credit_card', 'banking_billet']			
		this.configLigthbox(this.payments_forms)
	}

	configLigthbox(payments_forms){
		this.lightbox.lightbox(payments_forms);
	}

}