class TaskBulkCreate {
	constructor() {
	    this.nullData = {id: null, text: null};
		this.elInputPersonCustomer = $('[name=person_customer]');
		this.elCourtDistrict = $('[name=court_district]');
		this.elCourtDistrictComplemt = $('[name=court_district_complement]');
		this.elCity = $('[name=city]');
		this.elLawsuitNumber = $('[name=task_law_suit_number]');
		this.elFolderNumber = $('[name=folder_number]');
        this.elTypeTask = $('[name=type_task]');
        this.elMovement = $('[name=movement]');
        this.labelLawSuitNumber = $("label[for=id_task_law_suit_number]")
		this.onChangeCity();
		this.onChangeCourtDistrict();
		this.onChangeLawSuitNumber();
		this.onChangeTypeTask();
		this.onChangeFolderNumber();
        this.onSaveSubmit();
        this.elMovement.attr('disabled', true);
	}

	setSelect2(data, element) {
	    if(data.id && data.text) {
	        var newOption = new Option(data.text, data.id, true, true);
            element.append(newOption).trigger('change');
        }else{
	        element.val(null).trigger('change');
        }
    }
    
    get isHearing() {
        return this.elTypeTask.find(':selected').attr('is-hearing') === 'True';
    }

	get personCustomer() {
	    return this.elInputPersonCustomer.val();
    }

    set personCustomer(data) {
	    this.setSelect2(data, this.elInputPersonCustomer)
    }

    get city() {
	    return this.elCity.val();
    }

    get courtDistrict() {
	    return this.elCourtDistrict.val();
    }

    get lawSuitNumber() {
	    if (this.elLawsuitNumber.val().length > 0) {
            return this.elLawsuitNumber.val();
        }
        return false;
    }

    set lawSuitNumber(data) {
	    this.setSelect2(data, this.elLawsuitNumber);
    }

    get folderNumber() {
	    return this.elFolderNumber.val();
    }

    set folderNumber(data) {
	    this.setSelect2(data, this.elFolderNumber);
    }

    get movement() {
        return this.elMovement.val();
    }

    set movement(data) {
        this.setSelect2(data, this.elMovement);
    }

    async newPersonCustomer (csrfToken){
        const {value: personCustomerName} = await swal({
          title: 'Cadastro de Cliente/Parte',
          input: 'text',
          width: '30%',
          inputClass: 'form-control',
          inputPlaceholder: 'Nome',
          showCancelButton: true,
          inputValidator: (value) => {
            return new Promise((resolve) => {
              if (!value.trim()) {
                resolve('O nome é obrigatório!');
              } else {
                resolve();
              }

            });
          }
        });

        if (personCustomerName) {
            var data = {'legal_name': personCustomerName,
                     'name': personCustomerName,
                     'legal_type': 'J',
                     'is_customer': true
                };
            $.ajax({
                type: 'POST',
                url: '/person_customer/add/',
                data: data,
                success: (result)=>{
                    this.personCustomer = result;
                },
                error: (request, status, error)=>{
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings)=>{
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                dataType: 'json'
            });
        }
    }

	async newLawSuit (csrfToken, fields) {
	    var html_fields = '';
        fields.forEach(function(field){html_fields += field + '\n'});
	    const {value: formValues} = await swal({
            title: 'Cadastro de Processo',
            html: html_fields,
            width: '30%',
            focusConfirm: false,
            showCancelButton: true,
            showLoaderOnConfirm: true,
            preConfirm: () => {
                let typeLawsuit = document.getElementById("id_type_lawsuit").value;
                let lawsuitNumber = document.getElementById("id_law_suit_number").value;
                if (!typeLawsuit || !lawsuitNumber) {
                    swal.showValidationMessage('Campos obrigatórios não foram informados');
                    return false;
                }else if(!document.getElementById('id_person_customer').value){
                    swal.showValidationMessage('Favor selecionar um cliente');
                    return false;
                }else{
                    return {
                        typeLawsuit: typeLawsuit,
                        lawsuitNumber: lawsuitNumber
                    };
                }
            },
        });

        if (formValues) {
            let data = {'type_lawsuit': formValues.typeLawsuit,
                    'law_suit_number': formValues.lawsuitNumber,
                    'person_customer': document.getElementById('id_person_customer').value,
                    'folder_id': document.getElementById('id_folder_number').value
                };
            $.ajax({
                type: 'POST',
                url: '/processos/processos/task_bulk_create/',
                data: data,
                success: (result)=>{
                    this.lawSuitNumber = {id: result.id, text: result.text};
                    this.folderNumber = result.folder;
                },
                error: (request, status, error)=>{
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings)=>{
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                dataType: 'json'
            });
        }
    }

    async newFolder (csrfToken, fields) {
	    var html_fields = '';
        fields.forEach(function(field){html_fields += field + '\n'});
	    const {value: formValues} = await swal({
            title: 'Cadastro de Pasta',
            html: html_fields,
            width: '30%',
            focusConfirm: false,
            showCancelButton: true,
            showLoaderOnConfirm: true,
            preConfirm: () => {
                let personCustomer = document.getElementById("person_customer").dataset.value;
                if (!personCustomer) {
                    swal.showValidationMessage('Favor selecionar um Cliente');
                    return false;
                }else{
                    return personCustomer;
                }
            },
        });

        if (formValues) {
            let data = {'person_customer': formValues};
            $.ajax({
                type: 'POST',
                url: '/processos/pastas/task_bulk_create/',
                data: data,
                success: (result)=>{
                    this.folderNumber = result.folder;
                    this.personCustomer = result.person_customer;
                },
                error: (request, status, error)=>{
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings)=>{
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                dataType: 'json'
            });
        }
    }

	onChangeCity(){
	    this.elCity.on('change',()=>{
            if(this.city) {
                // a função clearTypeaheadField a seguir é definida como uma variável global no arquivo typeahead.js
                clearTypeaheadField(this.elCourtDistrict);
            }
        });
    }

	onChangeCourtDistrict(){
	    this.elCourtDistrict.on('change',()=>{
            if(this.courtDistrict) {
                // a função clearTypeaheadField a seguir é definida como uma variável global no arquivo typeahead.js
                clearTypeaheadField(this.elCity);
            }
        });
    }

	onChangeLawSuitNumber(){
	    this.elLawsuitNumber.on('change',()=>{
            this.movement = this.nullData;
            this.elMovement.attr('disabled', !this.lawSuitNumber);
        });
    }

	onChangeTypeTask(){
	    this.elTypeTask.on('change',()=>{
            if(this.isHearing){
                this.labelLawSuitNumber.addClass('ezl-required');
            }else{
                this.labelLawSuitNumber.removeClass('ezl-required');
            }
        });
    }

	onChangeFolderNumber(){
	    this.elFolderNumber.on('change',()=>{
            this.personCustomer = this.elFolderNumber.select2('data')[0].person_customer
        });
    }

    validateLawsuit() {
        if (this.isHearing && !this.lawSuitNumber) {
            swal({
                title: 'Campos obrigatórios não preenchidos', 
                html: 'É necessário informar processo para este tipo de serviço',
                type: 'error'
            });
        }

    }

    validateForm() {
        this.validateLawsuit();
    }

    save() {
        this.validateForm();
    }

    onSaveSubmit() {
        $('[type=submit]').on('click', (el)=> {                
            el.preventDefault();
            this.save();
        })
    }    
}
