class Billing {
	constructor(checkout) {		
		this.checkout = checkout;
		this.item;		
	}
	createCharge(csrfToken) {
		let data = this.item
		$.ajax({
			url: '/billing/charge/', 
			method: 'POST', 
			data: data, 
			success: (response) => {
				let charge_id = response.charge_id;
				this.checkout.openCheckout();
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
}