class Billing {
	constructor(checkout) {		
		this.checkout = checkout;
		this.item;		
	}
	createCharge(csrfToken) {
		let data = this.item;
		swal({
			title: 'Aguarde', 
			onOpen: () => {
				swal.showLoading()
			}
		});		
		$.ajax({
			url: '/billing/charge/', 
			method: 'POST', 
			data: data, 
			success: (response) => {
				let charge_id = response.charge_id;
				this.checkout.openCheckout(charge_id);
				swal.close();
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