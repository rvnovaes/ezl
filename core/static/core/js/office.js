class Office {
	constructor() {
		this._modalOfficeBasic = $('#modal-office-profile-basic');
		this._elBtnEditOffice = $('#btn-edit-office');
		this._elLegalName = document.querySelector('#el-office-legal-name');		
		this._elCpfCnpj = document.querySelector('#el-office-cpf-cnpj');
		this._elBtnSaveOffice = $('#btn-save-office');
		this.data;
		this.onClickBtnEditOffice();
		this.onClickBtnSaveOffice();
		this.setOffice();
	}

	get formOffice() {
		return $("#form-office");
	}

	get formData(){		
		return this.formOffice.serializeArray();
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
			this.updateAttr(key, this.data[key]);
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
			this.showOfficeForm();
		});
	}

	onClickBtnSaveOffice() {
		this._elBtnSaveOffice.on('click', ()=>{
			this.salvar();
		});
	}

	salvar() {
		this.formOffice.submit();
	}
}