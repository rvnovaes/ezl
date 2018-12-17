class Billing {
	constructor(lightbox) {
		this.lightbox=lightbox;
		this.items;
		this.payments_forms = ['credit_card'];			
		this.configLigthbox(this.payments_forms);		
		this.onClickPaymentButton();
	}

	configLigthbox(payments_forms){
		this.lightbox.lightbox(payments_forms);
	}

	onClickPaymentButton() {		
		this.lightbox.jq('#actionButton').on('click', (evt) => {
		  console.log(this.items);
          var data = {
          	customer: false,
          	shippingAddress: false,
            items: this.items,            
            actionForm: '/billing/payment/'
          };
          this.lightbox.show(data)			;
		})
	}

}