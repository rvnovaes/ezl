class TaskBulkCreate {
	constructor() {
	    this.formErrors = [];
	    this.nullData = {id: null, text: null};
		this.elInputPersonCustomer = $('[name=person_customer]');
		this.elCourtDistrict = $('[name=court_district]');
		this.elCourtDistrictComplemt = $('[name=court_district_complement]');
		this.elCity = $('[name=city]');
		this.elLawsuitNumber = $('[name=task_law_suit_number]');
		this.elFolderNumber = $('[name=folder_number]');
        this.elTypeTask = $('[name=type_task]');
        this.elMovement = $('[name=movement]');
        this.labelLawSuitNumber = $('label[for=id_task_law_suit_number]');
		this.onChangeCity();
		this.onChangeCourtDistrict();
		this.onChangeLawSuitNumber();
		this.onChangeTypeTask();
		this.onChangeFolderNumber();
        this.onSaveSubmit();
        this.onChangePersonCustomer();
        this.onChangeCourtDistrictComplement();
        this.elMovement.attr('disabled', true);
	}

	clearFormErrors(){
	    this.formErrors.splice(0, this.formErrors.length);
    }

    insertFormErrors(error, elements=[]){
        this.formErrors.push({field: elements,
                              message: error});
    }

    formatError(message){
	    return `<li>${message}</li>`
    }

    getErrors(){
	    let liErrors = ``;
        this.formErrors.forEach((error) => {
            liErrors += this.formatError(error.message );
        });
        return `
            <ul style="text-align: left;">
            ${liErrors}
            </ul>
        `;
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
	    this.setSelect2(data, this.elInputPersonCustomer);
    }

    get city() {
	    return this.elCity.val();
    }

    set city(data) {
	    this.setSelect2(data, this.elCity);
    }

    get courtDistrict() {
	    return this.elCourtDistrict.val();
    }

    set courtDistrict(data) {
	    this.setSelect2(data, this.elCourtDistrict);
    }

    get courtDistrictComplement() {
	    return this.elCourtDistrictComplemt.val();
    }

    set courtDistrictComplement(data) {
	    this.setSelect2(data, this.elCourtDistrictComplemt);
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
            onOpen: () => {
                let data = this.elInputPersonCustomer.select2('data')[0];
                this.setSelect2(data, $('[name=person_customer_swal]'));
            },
            preConfirm: () => {
                let personCustomer = document.getElementById('id_person_customer_swal').value;
                if (!personCustomer) {
                    swal.showValidationMessage('Favor selecionar um Cliente');
                    return false;
                }else{
                    return personCustomer;
                }
            },
        }).then(() => {console.log('teste');});

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
                this.courtDistrict = this.nullData;
            }
            this.elCourtDistrict.attr('disabled', !(!this.city));
            this.elCourtDistrictComplemt.attr('disabled', !(!this.city));
        });
    }

	onChangeCourtDistrict(){
	    this.elCourtDistrict.on('change',()=>{
            if(this.courtDistrict) {
                this.city = this.nullData;
                let courtDistrict = this.elCourtDistrictComplemt.select2('data')[0].court_district;
                if (courtDistrict && courtDistrict.id !== parseInt(this.courtDistrict)){
                    this.courtDistrictComplement = this.nullData;
                }
            }
            this.elCity.attr('disabled', !(!this.courtDistrict));
        });
    }

    onChangeCourtDistrictComplement(){
	    this.elCourtDistrictComplemt.on('change',()=>{
            if(this.courtDistrictComplement) {
                this.city = this.nullData;
                let courtDistrict = this.elCourtDistrictComplemt.select2('data')[0].court_district;
                if (courtDistrict) {
                    this.courtDistrict= courtDistrict;
                }
            }
            this.elCity.attr('disabled', !(!this.courtDistrict));
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
	        let personCustomer = this.elFolderNumber.select2('data')[0].person_customer;
	        if (personCustomer) {
	            this.personCustomer = personCustomer;
            }
        });
    }

	onChangePersonCustomer(){
	    this.elInputPersonCustomer.on('change',()=> {
	        let personCustomer = this.elFolderNumber.select2('data')[0].person_customer;
	        if (personCustomer && personCustomer.id !== parseInt(this.personCustomer)){
	            this.folderNumber = this.nullData;
            }
        });
    }

    validateLawsuit() {
        if (this.isHearing && !this.lawSuitNumber) {
            this.insertFormErrors('É necessário informar processo para este tipo de serviço',
                [this.elTypeTask, this.elLawsuitNumber]);
        }

    }

    validatePerformancePlace() {
        if (!(this.courtDistrict || this.city || this.courtDistrictComplement)) {
            this.insertFormErrors('Deve ser informada a comarca, o complemento ou a cidade para a solicitação da OS.',
                [this.elCourtDistrict, this.elCity, this.elCourtDistrictComplemt]);
        }

    }

    validateForm() {
	    this.clearFormErrors();
        this.validateLawsuit();
        this.validatePerformancePlace();
        if (this.formErrors.length <= 0) {
            return;
        }
        let htmlErrors = this.getErrors()
        swal({
            title: 'Campos obrigatórios não preenchidos',
            width: '45%',
            html: htmlErrors,
            type: 'error'
        });
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
