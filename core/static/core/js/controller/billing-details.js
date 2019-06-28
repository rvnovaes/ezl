class BillingDetail {
    constructor() {
        this._modalBillingDetail = $('#modal-office-profile-billing-details');
        this._elBtnAddBillingDetail = $('#btn-add-billing-detail');
        this._elBtnDeleteBillingDetail = $('#btn-delete-billing-detail');
        this._elInputZipcode = $('#form-billing-detail [name=zip_code]').mask('00000-000', {reverse: true});
        this._elInputPhoneNumber = $('#form-billing-detail [name=phone_number]').mask('(00) 00000-0000');
        this._elInputStreet = $('#form-billing-detail [name=street]');
		this._elInputAddressNumber = $('#form-billing-detail [name=number]');
		this._elInputCityRegion = $('#form-billing-detail [name=city_region]');
		this._elInputComplement = $('#form-billing-detail [name=complement]');
		this._elInputCity = $('#form-billing-detail [name=city]');
        this._elBillingDetailTable = $('#billing-details-table').DataTable({
            destroy: true,
            paging: false,
            dom: 'frti',
            language: {"url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"}
        });
        this.billingDetailSelected = [];
        this.onClickBtnAddBillingDetail();
        this.onClickBtnDeleteBillingDetail();
        this.onSubmitForm();
        this.onCheckItem();
        this.onClickTr();
        this.onChangeZipcode();
        this.onDocumentReady();
        this.createBillingAccountYapay()
    }

    static setSelect2(text, value, element) {
	    if(text && value) {
	        var newOption = new Option(text, value, true, true);
            element.append(newOption).trigger('change');
        }else{
	        element.val(null).trigger('change');
        }
    }

    static clearSelect2(element) {
        element.find(':selected').remove();
    }

    resetForm(){
        this.form.trigger('reset');
        BillingDetail.clearSelect2(this._elInputCity);
    }

    get form() {
		return $('#form-billing-detail');
	}

	get zipcode() {
		return this._elInputZipcode.cleanVal();
	}

	get street() {
		return this._elInputStreet.val();
	}

	set street(value) {
		this._elInputStreet.val(value);
	}

	get addressNumber() {
		return this._elInputAddressNumber.val();
	}

	get cityRegion() {
		return this._elInputCityRegion.val();
	}

	set cityRegion(value) {
		this._elInputCityRegion.val(value);
	}

	get addressComplement() {
		return this._elInputComplement.val();
	}

	set addressComplement(value) {
		this._elInputComplement.val(value);
	}

	get city() {
		return this._elInputCity.val();
	}

	set city(objCity) {
        BillingDetail.setSelect2(objCity.text, objCity.id, this._elInputCity);
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

	onClickBtnAddBillingDetail(){
		this._elBtnAddBillingDetail.on('click', ()=> {
			this.showForm();
		});
	}

	onClickBtnDeleteBillingDetail() {
		this._elBtnDeleteBillingDetail.on('click', ()=>{
			this.deleteBillingDetail();
		});
	}

	onCheckItem(){
		let self = this;
        $('#billing-details-table input:checkbox').on('change', function(){
            if ($(this).is(':checked')) {
                self.billingDetailSelected.push($(this).val());
            } else {
                self.billingDetailSelected.splice(self.billingDetailSelected.indexOf($(this).val(), 1));
            }
        });
	}

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
							showToast('success', `Detalhe de cobrança ${response.action} com sucesso`, '', 3000, true);
							self.hideForm();
							location.reload();
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

	setCityByZipCode(query){
        $.ajax({
            url: `city/zip_code/autocomplete_select2/`,
            method: 'GET',
            data: {q: query},
            success: (response)=>{
                this.city = response.results[0]
            }
        });
    }

	showForm() {
		this.form.attr(`action', '/billing/create_billing_detail/`);
        this.resetForm();
		this._modalBillingDetail.modal('show');
	}

	hideForm() {
		this._modalBillingDetail.modal('hide');
	}

	deleteBillingDetail() {
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
	  			url: '/billing/delete_billing_detail/',
	  			data: {ids: this.billingDetailSelected},
	            success: (response)=> {
	            	this.billingDetailSelected.forEach((row_id)=>{
	            		let tr = $(`#billing-details-table tr[id=${row_id}]`);
	            		this._elBillingDetailTable.row($(tr)).node().remove();
	            		this.checkBillingDetails();
	            	});
				    swal({
					      title: 'Detalhes de cobrança deletados com sucesso!',
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
		$( document ).ready(function(){
			if (!$(this).hasClass('selection')) {
				self.showForm();
				let id = $("#billing_detail_id").val();
				if(id) {
					$.ajax({
						url: `/billing/get_billing_detail/${id}/`,
						method: 'GET',
						success: (response)=>{
							self.form.attr('action', `/billing/update_billing_detail/${response.id}/`);
							Object.keys(response.billing_address).forEach((key)=>{
								if (key === 'city') {
									self.city = {text: response.billing_address['city_name'],
										id: response.billing_address[key]};
								} else {
									self.form.find(`[name=${key}]`).val(response.billing_address[key])
								}
							});
							Object.keys(response).forEach((key)=>{
								self.form.find(`[name=${key}]`).val(response[key])
							});
						}
					});
				}
			}
		});
	}

	onChangeZipcode() {
		this._elInputZipcode.on('change', (evt)=> {
			$.ajax({
				method: 'GET',
				url: `https://viacep.com.br/ws/${this.zipcode}/json/unicode/`,
				success: (response)=>{
					debugger;
				    this.setCityByZipCode(`${response.localidade}|${response.uf}`);
					this.street = response.logradouro;
					this.cityRegion = response.bairro;
					this.addressComplement = response.complemento;
				}
			});
		});
	}

	checkBillingDetails() {
		$.ajax({
			method: 'GET',
			url: `/billing/get_office_billing_detail/`,
			success: (response)=>{
				if (response.id){
					this._elBtnAddBillingDetail.prop('disabled', true);
				} else {
				    this._elBtnAddBillingDetail.prop('disabled', false);
                }
			}
		});
	}

	createBillingAccountYapay(){
    	$('#btn-yapay-billing-detail').on('click', function(){
			let account_type = "1";
			let trade_name = $("#trade_name").val();
			let company_name = $("#legal_name").val();
			let cnpj = $("#legal_cnpj").val();
			let email = $("#id_email").val();
			let name = $("#id_full_name").val();
			let cpf = $("#id_cpf").val();
			let type_contact = $("#id_type_contact").val();
			let number_contact = $("#id_phone_number").val().replace("(","").replace(")","").replace("-","").replace(" ", "");
		    let street = $("#id_street").val();
		    let number = $("#id_number").val();
		    let type_address = "B";
		    let neighborhood = $("#id_city_region").val();
		    let completion = $("#id_complement").val();
		    let postal_code = $("#id_zip_code").val().replace("-","");
    		let city_split = $("#id_city option:selected").html().split("-");
    		let city_name = $.trim(city_split[0]);
			let city_uf = $.trim(city_split[1]);
			let password = $("#id_password").val();

			let payload = {
				"account_type": account_type,
				"trade_name": trade_name,
				"company_name": company_name,
				"cnpj": cnpj,
				"email": email,
				"name": name,
				"cpf": cpf,
				"contacts": [
				{
					"type_contact":type_contact,
					"number_contact": number_contact
				}],
				"street": street,
				"number": number,
				"type_address": type_address,
				"neighborhood": neighborhood,
				"completion": completion,
				"postal_code": postal_code,
				"city": city_name,
				"state": city_uf,
				"password": password
			};
			if(password.length < 4){
				showToast('error', `Campo senha deve ter no mínimo 4 dígitos `, '', 3000, true);
			}else {
				$.ajax({
					url: "http://142.93.204.204:8010/api/clientes/",
					method: 'POST',
					dataType: "json",
					contentType: "application/json; charset=utf-8",
					headers: {
						"Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluaXN0cmF0aXZvQGV6cGF5LmNvbSIsImV4cCI6MTU2MTY2MTYyMiwiZW1haWwiOiJhZG1pbmlzdHJhdGl2b0BlenBheS5jb20ifQ.WwreazU4PtVfg-b79H2i0YcTOF9UEjJcdzbPDkHQNJk"
					},
					data: JSON.stringify(payload),
					success: (response) => {
						showToast('success', `Cliente cadastrado na Yapay com sucesso`, '', 3000, true);
					},
					error: (response) => {
						let errors = response.responseJSON;
						let msgerrors = [];
						for(i = 0; i< errors.length; i++){
							msgerrors.push(errors[i].validation_errors[i].message_complete);
						}
						if (response.status == 400) {
							showToast('error', `Não foi possível realizar o cadastro - ${ msgerrors }`, '', 6000, true);
						}
					}
				});
			}
		});
	}

	onDocumentReady(){
	    $(document).ready(()=>{
			this.checkBillingDetails();
        });
    }
}