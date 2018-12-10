class Address {
	constructor(officeId) {
		this.officeId = officeId;
		this._modalOfficeAddress = $('#modal-office-profile-address');
		this._elBtnAddAddress = $('#btn-add-address');
		this._elBtnDeleteAddress = $('#btn-delete-address');
		this.elCity = $('[name=city]');
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
		this.onClickTr();		
	}

	get form() {
		return $("#form-address")
	}	

	setSelect2(text, value, element) {
	    if(text && value) {
	        var newOption = new Option(text, value, true, true);
            element.append(newOption).trigger('change');
        }else{
	        element.val(null).trigger('change');
        }
    }	

	get query() {
		let formData = this.form.serializeArray();
		let data = {};
		$(formData).each((index, obj) =>{
		        data[obj.name] = obj.value;
		    });
		this.form.find('input[type=checkbox]').each(function(){
			data[$(this).attr('name')] = $(this).prop('checked')
		})				
		return data;
	}


	onClickBtnAddAddress(){
		this._elBtnAddAddress.on('click', ()=> {
			this.showOfficeAddressForm();
		})
	}

	showOfficeAddressForm() {
		this.form.attr(`action', '/office_profile_address_create/${this.officeId}/`)
		this._modalOfficeAddress.modal('show');
	};	    

	hideOfficeAddressForm() {
		this._modalOfficeAddress.modal('hide');
	};	

	onSubmitForm() {
		this.form.on('submit', (event)=>{	
			event.preventDefault();		
			let action = this.form.attr('action');
			let self = this;
			swal({
				title: 'Aguarde',
				onOpen() {
					swal.showLoading();					
					$.ajax({
						method: 'POST',
						url: action, 
						data: self.query,
						success: (response)=> {
							swal.close();
							showToast('success', 'Perfil atualizado com sucesso', '', 3000, true);							
							self.hideOfficeAddressForm();
							location.reload();
						}, 
						error: (request, status, error)=> {
							Object.keys(request.responseJSON.errors).forEach((key)=>{
								request.responseJSON.errors[key].forEach((e)=>{
									swal.close();
									showToast('error', self.form.find(`[name=${key}]`).siblings('label').text(), e, 0, false);
								})
							})																				
						}
					})					
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

	onClickTr(){
		let self = this;
		$(`#address-table tr`).on('click', function(event){						
			$(event.currentTarget).parent()			
			self.showOfficeAddressForm(); 
			let addressId = $(this).attr('id');
			$.ajax({
				url: `/office_profile_address_data/${addressId}/`, 
				method: 'GET', 
				success: (response)=>{
					self.form.attr('action', `/office_profile_address_update/${response.id}/`)					
					Object.keys(response).forEach((key)=>{
						if (key == 'city') {
							self.setSelect2(response['city_name'], response[key], self.elCity)							
						}
						if (typeof response[key] == 'boolean') {
							self.form.find(`[name=${key}]`).prop('checked', response[key]);
						} else {
							self.form.find(`[name=${key}]`).val(response[key])
						}
					})
				}
			})
		})
	}

}