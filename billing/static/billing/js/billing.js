class Billing {
	constructor() {
		//this.lightbox=lightbox;
		this.item;
		this.payments_forms = ['credit_card'];			
		//this.configLigthbox(this.payments_forms);		
	}

/*	configLigthbox(payments_forms){
		this.lightbox.lightbox(payments_forms);
	}*/

	createCharge(csrfToken) {
		let data = this.item
		$.ajax({
			url: '/billing/charge/', 
			method: 'POST', 
			data: data, 
			success: (response) => {
			    window.open(response.url, '_blank');			    
			}, 
			error: (error)=>{
				console.log(error)
			},
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            dataType: 'json'			
		})
	}

	// onClickPaymentButton() {		
	// 	this.lightbox.jq('#actionButton').on('click', (evt) => {
	// 	  console.log(this.items);
 //          var data = {
 //          	customer: false,
 //          	shippingAddress: false,
 //            items: this.items,            
 //            actionForm: '/billing/payment/'
 //          };
 //          this.lightbox.show(data)			;
	// 	})
	// }

}