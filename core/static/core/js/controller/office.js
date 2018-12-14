class Office {
	constructor(office_id) {
		this.office_id = office_id;
		this._modalOfficeBasic = $('#modal-office-profile-basic');
		this._elBtnEditOffice = $('#btn-edit-office');
		this._elLegalName = document.querySelector('#el-office-legal-name');		
		this._elCpfCnpj = document.querySelector('#el-office-cpf-cnpj');
		this._elBtnSaveOffice = $('#btn-save-office');
		this.data;
		this.onClickBtnEditOffice();		
		this.setOffice();
		this.onSubmitForm();
	};	

	get form() {
		return $("#form-office")
	}

	get formData(){		
		return this.form.serializeArray();
	}

	get query() {
		let formData = this.formData;
		let data = {};
		$(formData ).each((index, obj) =>{
		        data[obj.name] = obj.value;
		    });		
		return data;
	}	

	get legalName(){
		return this._elLegalName.textContent
	}

	set legalName(value){
		this.data.legal_name = this._elLegalName.textContent = value;
	}

	get cpfCnpj() {
		return this._elCpfCnpj.textContent;
	}

	set cpfCnpj(value) {
		this.data.cpf_cnpj = this._elCpfCnpj.textContent = value;
	}	


	formatAttr(stringVariable) {
		return stringVariable.replace(/_([a-z])/g, function (m, w) {
		    return w.toUpperCase();
		});		
	}

	updateInstance(name, value) {
		Object.keys(this.data).forEach((key)=>{
			this.updateAttr(key, this.data[key])
		});
	}

	updateAttr(name, value) {
		this[this.formatAttr(name)] = value;
	}


	setOffice(){
		$.ajax({
			url: '/office_profile_data/', 
			method: 'GET', 
			success: (response) => {
				this.data = response;
				this.updateInstance();
			}
		});
	}

	showOfficeForm() {
		this._modalOfficeBasic.modal('show');
	}

	hideOfficeForm() {
		this._modalOfficeBasic.modal('hide');
	}

	onClickBtnEditOffice() {
		this._elBtnEditOffice.on('click', ()=>{
			console.log('aqui');
			this.showOfficeForm();
		});
	}

	onCheckItem(){
		let self = this;
        $('#os-table input:checkbox').on('change', function(){
            if ($(this).attr('id') === 'checkAll') {
                if ($(this).is(':checked')) {
                    self.tasksToPay = self.allTaskIds
                } else {
                    self.tasksToPay = [];
                }
            } else {
                if ($(this).is(':checked')) {
                    self.tasksToPay.push($(this).val());
                } else {
                    self.tasksToPay.splice(self.tasksToPay.indexOf($(this).val(), 1));
                }                            
            }
        });
	}	

	onSubmitForm() {
		this.form.on('submit', (event)=>{			
			event.preventDefault();
			swal({
				title: 'Aguarde',
				onOpen: ()=> {
					swal.showLoading();					
					$.ajax({
						method: 'POST',
						url: "/office_profile_update/" + this.office_id + "/", 
						data: this.form.serialize(),
						success: (response)=> {
							swal.close();
							showToast('success', 'Perfil atualizado com sucesso', '', 3000, true);
							this.setOffice();
							this.hideOfficeForm();
						}, 
						error: (request, status, error)=> {
							Object.keys(request.responseJSON.errors).forEach((key)=>{
								request.responseJSON.errors[key].forEach((e)=>{
									swal.close();
									showToast('error', this.form.find(`[name=${key}]`).siblings('label').text(), e, 0, false);
								});
							});
						}
					});
				}
			});
		});
	}
}