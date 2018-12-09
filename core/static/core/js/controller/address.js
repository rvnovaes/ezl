class Address {
	constructor() {
		this._modalOfficeAddress = $('#modal-office-profile-address');
		this._elBtnAddAddress = $('#btn-add-address');
		this._elBtnDeleteAddress = $('#btn-delete-address');
		this._elAddressTable = $('#address-table').DataTable({
			destroy: true,
            paging: false,
            dom: 'frti',
            language: {"url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"}
        });
                            
		this.addressSelected = [];
		this.onClickBtnAddAddress();
		this.onClickBtnDeleteAddress();
		this.onSubmitForm();
		this.onCheckItem();
	}

	get form() {
		return $("#form-address")
	}	

	onClickBtnAddAddress(){
		this._elBtnAddAddress.on('click', ()=> {
			this.showOfficeAddressForm();
		})
	}

	showOfficeAddressForm() {
		this._modalOfficeAddress.modal('show');
	};	    

	hideOfficeAddressForm() {
		this._modalOfficeAddress.modal('hide');
	};	

	onSubmitForm() {
		this.form.on('submit', (event)=>{			
			swal({
				title: 'Aguarde',
				onOpen() {
					swal.showLoading();
				}
			})
		})
	}

	onClickBtnDeleteAddress() {
		this._elBtnDeleteAddress.on('click', ()=>{
			this.deleteAddress();
		})
	}

	onCheckItem(){
		let self = this;
        $('#address-table input:checkbox').on('change', function(){
            if ($(this).is(':checked')) {
                self.addressSelected.push($(this).val())    
            } else {
                self.addressSelected.splice(self.addressSelected.indexOf($(this).val(), 1))
            }                            
        })		
	}	

	deleteAddress() {
		swal({
		  title: 'Esta operação é irreversível',
		  text: "Deseja realmente deletar!",
		  type: 'warning',
		  showCancelButton: true,
		  confirmButtonColor: '#3085d6',
		  cancelButtonColor: '#d33',
		  confirmButtonText: 'Sim, quero deletar!'
		}).then((result) => {
		  if (result.value) {
	  		$.ajax({
	  			method: 'POST',
	  			url: '/office_profile_address_delete/', 
	  			data: {ids: this.addressSelected}, 
	            success: (response)=> {
	            	this.addressSelected.forEach((row_id)=>{
	            		let tr = $(`#address-table tr[id=${row_id}]`);
	            		this._elAddressTable.row($(tr)).node().remove();
	            	});
				    swal({
					      title: 'Endereços deletados com sucesso!',				      
					      type: 'success'				    	
				    	}
				    )	                
	            },
	            beforeSend: function (xhr, settings) {
	                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
	            },
	            dataType: 'json'	  			
	  		})
		  }
		})
	}	

}