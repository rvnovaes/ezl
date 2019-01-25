class ContactMechanism {
	constructor(officeId) {
		this.officeId = officeId;
		this._modalOfficeContactMechanism = $('#modal-office-profile-contact-mechanism');
		this._elBtnAddContactMechanism = $('#btn-add-contact-mechanism');
		this._elBtnDeleteContactMechanism = $('#btn-delete-contact-mechanism');
		this._elContactMechanismTable = $('#contact-mechanism-table').DataTable({
			destroy: true,
            paging: false,
            dom: 'frti',
            language: {"url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"}
        });		
		this.contactMechanismSelected = [];
		this.onClickBtnContactMechanism();
		this.onSubmitForm();
		this.onCheckItem();
		this.onClickBtnDeleteContactMechanism();
		this.onClickTr();
	}

	get form() {
		return $("#form-contact-mechanism")
	}	


	get query() {
		let formData = this.form.serializeArray();
		let data = {};
		$(formData).each((index, obj) =>{
		        data[obj.name] = obj.value;
		    });
		this.form.find('input[type=checkbox]').each(function(){
			data[$(this).attr('name')] = $(this).prop('checked')
		});
		return data;
	}	

	onClickBtnContactMechanism(){
		this._elBtnAddContactMechanism.on('click', ()=> {
			this.showOfficeContactMechanismForm();
		})
	}

	showOfficeContactMechanismForm() {
		this.form.attr(`action', '/office_profile_contact_mechanism_create/${this.officeId}/`)
		this._modalOfficeContactMechanism.modal('show');
	};	    

	hideOfficeContactMechanismForm() {
		this._modalOfficeContactMechanism.modal('hide');
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
							location.reload();
							showToast('success', 'Perfil atualizado com sucesso', '', 3000, true);
						}, 
						error: (request, status, error)=> {
							Object.keys(request.responseJSON.errors).forEach((key)=>{
								request.responseJSON.errors[key].forEach((e)=>{
									swal.close();
									showToast('error', self.form.find(`[name=${key}]`).siblings('label').text(), e, 0, false);
								});
							});
						}
					});
				}
			});
		});
	}

	onClickBtnDeleteContactMechanism() {
		this._elBtnDeleteContactMechanism.on('click', ()=>{
			this.deleteContactMechanism();
		});
	}

	onCheckItem(){
		let self = this;
        $('#contact-mechanism-table input:checkbox').on('change', function(){
            if ($(this).is(':checked')) {
                self.contactMechanismSelected.push($(this).val());
            } else {
                self.contactMechanismSelected.splice(self.contactMechanismSelected.indexOf($(this).val(), 1));
            }                            
        });
	}			

	deleteContactMechanism() {
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
	  			url: '/office_profile_contact_mechanism_delete/', 
	  			data: {ids: this.contactMechanismSelected}, 
	            success: (response) => {
	            	this.contactMechanismSelected.forEach((row_id)=>{
	            		let tr = $(`#contact-mechanism-table tr[id=${row_id}]`);
	            		this._elContactMechanismTable.row($(tr)).node().remove();
	            	});	            	
				    swal({
					      title: 'Contatos deletados com sucesso!',				      
					      type: 'success'				    	
				    	}
				    );
	            },
	            beforeSend: function (xhr, settings) {
	                xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
	            },
	            dataType: 'json'	  			
	  		});
		  }
		});
	}

	onClickTr(){
		let self = this;
		$(`#contact-mechanism-table tr`).on('click', function(event){			
			self.showOfficeContactMechanismForm(); 
			let contactMechanismId = $(this).attr('id');
			$.ajax({
				url: `/office_profile_contact_mechanism_data/${contactMechanismId}/`, 
				method: 'GET', 
				success: (response)=>{
					self.form.attr('action', ('action', `/office_profile_contact_mechanism_update/${response.id}/`))
					Object.keys(response).forEach((key)=>{
						if (typeof response[key] == 'boolean') {
							self.form.find(`[name=${key}]`).prop('checked', response[key]);
						} else {
							self.form.find(`[name=${key}]`).val(response[key]);
						}
					});
				}
			});
		});
	}

}