class Office {
	constructor(office_id) {
		this.office_id = office_id;
		this._modalOfficeBasic = $('#modal-office-profile-basic');
		this._elBtnEditOffice = $('#btn-edit-office');
		this._elLegalName = document.querySelector('#el-office-legal-name');		
		this._elCpfCnpj = document.querySelector('#el-office-cpf-cnpj');
		this._elBtnSaveOffice = $('#btn-save-office');
		this._elImgLogo = $('#logo');
		this.data;
		this.onClickBtnEditOffice();		
		this.setOffice();
		this.onSubmitForm();
	}

	get form() {
		return $("#form-office");
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
		return this._elLegalName.textContent;
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

	static formatCpfCnpj(cpfCnpj){
		cpfCnpj.replace(/[^0-9]+/g, '');
		if (cpfCnpj.length <= 11) {
			return `${cpfCnpj.substr(0,3)}.${cpfCnpj.substr(3,3)}.${cpfCnpj.substr(6,3)}-${cpfCnpj.substr(9)}`;
		} else {
			return `${cpfCnpj.substr(0,2)}.${cpfCnpj.substr(2,3)}.${cpfCnpj.substr(5,3)}/`+
				`${cpfCnpj.substr(8,4)}-${cpfCnpj.substr(12)}`;
		}
	}


	formatAttr(stringVariable) {
		return stringVariable.replace(/_([a-z])/g, function (m, w) {
		    return w.toUpperCase();
		});		
	}

	updateInstance(name, value) {
		if (this.data.cpf_cnpj !== ''){
			this.data.cpf_cnpj = Office.formatCpfCnpj(this.data.cpf_cnpj);
		}
		Object.keys(this.data).forEach((key)=>{
		    if (key !== 'logo') {
                this.updateAttr(key, this.data[key]);
            } else {
		    	this._elImgLogo.attr('src', this.data[key]);
			}
		});
	}

	updateAttr(name, value) {
		this[this.formatAttr(name)] = value;
	}


	setOffice(){
		$.ajax({
			url: `/office_profile_data/${this.office_id}`,
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
			this.showOfficeForm();
		});
	}

	onCheckItem(){
		let self = this;
        $('#os-table input:checkbox').on('change', function(){
            if ($(this).attr('id') === 'checkAll') {
                if ($(this).is(':checked')) {
                    self.tasksToPay = self.allTaskIds;
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
			var formdata = false;
            if (window.FormData){
                formdata = new FormData(this.form[0]);
            }

            swal({
				title: 'Aguarde',
				onOpen: ()=> {
					swal.showLoading();					
					$.ajax({
                        contentType: false,
                        cache: false,
                        processData: false,
						method: 'POST',
						url: "/office_profile_update/" + this.office_id + "/", 
						data: formdata ? formdata : this.form.serialize(),
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