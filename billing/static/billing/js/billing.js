class Billing {
	constructor(lightbox) {
		this.lightbox=lightbox;
		this.payments_forms = ['credit_card', 'banking_billet']			
		this.configLigthbox(this.payments_forms)
		this.onClickPaymentButton()
	}

	configLigthbox(payments_forms){
		this.lightbox.lightbox(payments_forms);
	}

	onClickPaymentButton() {
		this.lightbox.jq('#actionButton').click((evt)=>{
          var data = {
            items: [
              {
                name: 'Item 1', // nome do item, produto ou serviço
                value: 12000 // valor (12000 = R$ 120,00)
              },
            ],
            shippingCosts: 3560,
            actionForm: 'http://your_domain/your_backend_url'
          };
          this.lightbox.show(data)			;
		})
	}

}