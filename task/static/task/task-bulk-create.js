class TaskBulkCreate {
	constructor() {
	    this.formErrors = [];
	    this.nullData = {id: null, text: null};
	    this.defaultPersonAskedBy = null;
	    this.enableOnChange = true;
	    this.baseURL = '';
	    this.taskID = null;
		this.elInputPersonCustomer = $('[name=person_customer]');
		this.elCourtDistrict = $('[name=court_district]');
		this.elCourtDistrictComplemt = $('[name=court_district_complement]');
		this.elCity = $('[name=city]');
		this.elLawsuitNumber = $('[name=task_law_suit_number]');
		this.elFolderNumber = $('[name=folder_number]');
        this.elTypeTask = $('[name=type_task]');
        this.elMovement = $('[name=movement]');
        this.elFinalDeadlineDate = $('[name=final_deadline_date]');
        this.elPerformancePlace = $('#id_performance_place');
        this.elPersonAskedBy = $('#id_person_asked_by');
        this.labelLawSuitNumber = $('label[for=id_task_law_suit_number]');
        this.elBtnAddFolder = $("#btn_add_folder");
		this.onChangeCity();
		this.onChangeCourtDistrict();
		this.onChangeLawSuitNumber();
		this.onChangeTypeTask();
		this.onChangeFolderNumber();
        this.onSaveSubmit();
        this.onChangePersonCustomer();
        this.onChangeCourtDistrictComplement();
        this.onDocumentReady();
	}

	static removeErrorClass(field=null){
	    if (!field){
	        $('.error').each(function () {
                $(this).removeClass('error');
            });
        }else{
	        field.removeClass('error');
        }
    }

    static addErrorClass(field){
	    if (!field){
	        return;
        }
        // $(task.elInputPersonCustomer.data('select2').$selection).addClass('error')
        if(field.data('select2')) {
            $(field.data('select2').$selection).addClass('error');
        }else{
            field.addClass('error');
        }
    }

	clearFormErrors(){
	    this.formErrors.splice(0, this.formErrors.length);
        TaskBulkCreate.removeErrorClass();
    }

    insertFormErrors(error, elements=[]){
        this.formErrors.push({field: elements,
                              message: error});
    }

    static formatError(message){
	    return `<li>${message}</li>`
    }

    getErrors(){
	    let liErrors = ``;
        this.formErrors.forEach((error) => {
            error.field.forEach((field) => TaskBulkCreate.addErrorClass(field));
            liErrors += TaskBulkCreate.formatError(error.message );
        });
        return `
            <ul style="text-align: left;">
            ${liErrors}
            </ul>
        `;
    }

	static setSelect2(data, element) {
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
	    TaskBulkCreate.setSelect2(data, this.elInputPersonCustomer);
    }

    get typeTask() {
	    return this.elTypeTask.val();
    }

    setPerformancePlace() {
	    let performancePlace = '';
	    let courtDistrictComplement = this.courtDistrictComplementText;
	    let courtDistrict = this.courtDistrictText;
	    let city = this.cityText;
	    if (courtDistrictComplement){
	        performancePlace = courtDistrictComplement;
        }else if(courtDistrict){
	        performancePlace = courtDistrict;
        }else if(city){
	        performancePlace = city;
        }
        this.elPerformancePlace.val(performancePlace);
    }

    get performancePlace() {
	    this.setPerformancePlace();
	    return this.elPerformancePlace.val();
    }

    get finalDeadlineDate() {
	    return this.elFinalDeadlineDate.val();
    }

    get cityText() {
	    return (this.city) ? this.elCity.select2('data')[0].text : '';
    }

    get city() {
	    return this.elCity.val();
    }

    set city(data) {
	    TaskBulkCreate.setSelect2(data, this.elCity);
    }

    get courtDistrictText() {
	    return (this.courtDistrict) ? this.elCourtDistrict.select2('data')[0].text : '';
    }

    get courtDistrict() {
	    return this.elCourtDistrict.val();
    }

    set courtDistrict(data) {
	    TaskBulkCreate.setSelect2(data, this.elCourtDistrict);
    }

    get courtDistrictComplementText() {
	    return (this.courtDistrictComplement) ? this.elCourtDistrictComplemt.select2('data')[0].text : '';
    }

    get courtDistrictComplement() {
	    return this.elCourtDistrictComplemt.val();
    }

    set courtDistrictComplement(data) {
	    TaskBulkCreate.setSelect2(data, this.elCourtDistrictComplemt);
    }

    get lawSuitNumber() {
	    if (this.elLawsuitNumber.val().length > 0) {
            return this.elLawsuitNumber.val();
        }
        return false;
    }

    get lawSuitNumberData() {
	    return this.elLawsuitNumber.select2('data')[0];
    }

    set lawSuitNumber(data) {
	    TaskBulkCreate.setSelect2(data, this.elLawsuitNumber);
    }

    get folderNumber() {
	    return this.elFolderNumber.val();
    }

    set folderNumber(data) {
	    TaskBulkCreate.setSelect2(data, this.elFolderNumber);
    }

    get movement() {
        return this.elMovement.val();
    }

    set movement(data) {
        TaskBulkCreate.setSelect2(data, this.elMovement);
    }

    getTaskURL(){
	    return `${this.baseURL}/dashboard/${this.taskID}/`;
    }

    getActionTaskURL(action){
	    return `${this.getTaskURL()}?action=${action}`;
    }

    htmlConfirmSwal(result){
	    return `
            Número da OS: <a href="${this.getTaskURL()}" target="_blank">${result.task_number}</a>
            <br />
            <div class="row">
                <div class="col-md-7 col-md-offset-3">                    
                    <button type="button" id="delegateOS" class="text-white btn btn-ezl-open btn-block m-b-10 m-t-10" style="padding-left: 0px;">
                        <span class="btn-label" style="margin-left: -35px;">
                            <i class="fa fa-building-o"></i>
                        </span> Delegar
                    </button>                
                </div>
            </div>
            <div class="row">
                <div class="col-md-7 col-md-offset-3">
                    <button type="button" id="assignOS"  class="text-white btn btn-info btn-block m-b-10 m-t-10" style="padding-left: 0px;">
                        <span class="btn-label" style="margin-left: -35px;">
                            <i class="mdi mdi-account-location"></i>
                        </span> Atribuir
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-7 col-md-offset-3">
                    <button type="button" id='createOS' class="text-white btn create-os-active btn-block m-b-10 m-t-10" style="padding-left: 0px;">
                        <span class="btn-label" style="margin-left: 0;"> 
                            <i class="mdi mdi-plus-circle-outline"></i>
                        </span> Criar outra OS
                    </button>
                </div>                
            </div>                            
            `;
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
                TaskBulkCreate.setSelect2(data, $('[name=person_customer_swal]'));
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
        });

        if (formValues) {
            let data = {'person_customer': formValues};
            $.ajax({
                type: 'POST',
                url: '/processos/pastas/task_bulk_create/',
                data: data,
                success: (result)=>{
                    this.folderNumber = result.folder;
                    if(parseInt(this.personCustomer) !== parseInt(result.person_customer.id)){
                        this.personCustomer = result.person_customer;
                    }
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
            if(this.enableOnChange) {
                if (this.city) {
                    this.courtDistrict = this.nullData;
                }
                this.elCourtDistrict.attr('disabled', !(!this.city));
                this.elCourtDistrictComplemt.attr('disabled', !(!this.city));
            }
        });
    }

	onChangeCourtDistrict(){
	    this.elCourtDistrict.on('change',()=>{
            if(this.enableOnChange){
                if(this.courtDistrict) {
                    this.city = this.nullData;
                    let courtDistrict = this.elCourtDistrictComplemt.select2('data')[0].court_district;
                    if (courtDistrict && courtDistrict.id !== parseInt(this.courtDistrict)){
                        this.courtDistrictComplement = this.nullData;
                    }
                    this.folderNumber = this.nullData;
                    this.enableOnChange = false;
                    this.lawSuitNumber = this.nullData;                    
                    this.enableOnChange = true;
                } else {
                    this.enableOnChange = false;
                    this.lawSuitNumber = this.nullData
                    this.folderNumber = this.nullData
                    this.enableOnChange = true;
                }

                this.elCity.attr('disabled', !(!this.courtDistrict));
            }
        });
    }

    onChangeCourtDistrictComplement(){
	    this.elCourtDistrictComplemt.on('change',()=>{
            if(this.enableOnChange){
                if(this.courtDistrictComplement) {
                    this.city = this.nullData;
                    let courtDistrict = this.elCourtDistrictComplemt.select2('data')[0].court_district;
                    if (courtDistrict) {
                        this.courtDistrict= courtDistrict;
                    }
                }
                this.elCity.attr('disabled', !(!this.courtDistrict));
            }
        });
    }

	onChangeLawSuitNumber(){
	    this.elLawsuitNumber.on('change',()=>{
	        if (this.enableOnChange) {
                this.movement = this.nullData;
                this.elMovement.attr('disabled', !this.lawSuitNumber);
                this.elBtnAddFolder.attr('disabled', false);
                if (this.lawSuitNumber) {
                    this.enableOnChange = false;
                    let personCustomer = this.lawSuitNumberData.person_customer;
                    if (personCustomer && personCustomer.id) {
                        this.personCustomer = personCustomer;
                    }
                    let folder = this.lawSuitNumberData.folder;
                    if (folder && !folder.isDefault) {
                        this.folderNumber = folder;
                        this.elBtnAddFolder.attr('disabled', true);
                    }
                    let courtDistrict = this.lawSuitNumberData.court_district;
                    if (courtDistrict && courtDistrict.id) {
                        this.courtDistrict = courtDistrict;
                    }
                    let courtDistrictComplement = this.lawSuitNumberData.court_district_complement;
                    if (courtDistrictComplement && courtDistrictComplement.id) {
                        this.courtDistrictComplement = courtDistrictComplement;
                    }
                    let city = this.lawSuitNumberData.city;
                    if (city && city.id) {
                        this.city = city;
                    }
                    this.enableOnChange = true
                } else {
                    this.courtDistrict = this.nullData;
                    this.city = this.nullData;
                    this.courtDistrictComplement = this.nullData
                }
            }
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
	        if (this.enableOnChange) {
                let personCustomer = this.elFolderNumber.select2('data')[0].person_customer;
                if (personCustomer) {
                    this.personCustomer = personCustomer;
                }
            }
        });
    }

	onChangePersonCustomer(){
	    this.elInputPersonCustomer.on('change',()=> {            
	        if(this.enableOnChange){
	            let personCustomer = this.elFolderNumber.select2('data')[0].id;
                if (personCustomer && personCustomer.id !== parseInt(this.personCustomer)){
                    this.folderNumber = this.nullData;
                }
                this.lawSuitNumber = this.nullData;
            }
        });
    }

    validatePersonCustomer() {
        if (!this.personCustomer) {
            this.insertFormErrors('É necessário informar um cliente.',
                [this.elInputPersonCustomer]);
        }

    }

    validateTypeTask() {
        if (!this.typeTask) {
            this.insertFormErrors('É necessário informar um tipo de serviço.',
                [this.elTypeTask]);
        }

    }

    validateLawsuit() {
        if (this.isHearing && !this.lawSuitNumber) {
            this.insertFormErrors('É necessário informar processo para este tipo de serviço.',
                [this.elTypeTask, this.elLawsuitNumber]);
        }

    }

    validatePerformancePlace() {
        if (!(this.courtDistrict || this.city || this.courtDistrictComplement)) {
            this.insertFormErrors('Deve ser informada a comarca, o complemento ou a cidade para a solicitação da OS.',
                [this.elCourtDistrict, this.elCity, this.elCourtDistrictComplemt]);
        }

    }

    validateFinalDeadlineDate() {
        if (!this.finalDeadlineDate) {
            this.insertFormErrors('Deve ser informado o prazo de cumprimento da OS.',
                [this.elFinalDeadlineDate]);
        }
        if (moment().add(2, 'hour') > moment(this.finalDeadlineDate, "DD/MM/YYYY HH:mm")){
            this.insertFormErrors('O prazo de cumprimento da OS é inferior a duas horas.',
                [this.elFinalDeadlineDate]);
        }

    }

    submitForm(data){
	    this.baseURL = window.location.origin;
	    TaskBulkCreate.swalLoading('Criando a OS');
        $.ajax({
            type: 'POST',
            url: window.location,
            data: data,
            success: (result)=>{
                this.taskID = result.task_id;
                swal.close();
                let html = this.htmlConfirmSwal(result);
                swal({
                    title: 'OS criada com sucesso',
                    type: 'success',
                    html: html,
                    showCloseButton: true,
                    showCancelButton: false,
                    showConfirmButton: false,
                    onClose: () => {
                        window.location.reload();
                    }
                });
                $('#createOS').click(()=>{
                    window.location.reload();
                });
                $('#delegateOS').click(()=>{
                    this.delegateTask();
                });
                $('#assignOS').click(()=>{
                    this.assignTask();
                });
            },
            error: (request, status, error)=>{
                swal.close();
                showToast('error', 'Atenção', error, 0, false);
            },
            beforeSend: (xhr, settings)=>{
                xhr.setRequestHeader('X-CSRFToken', data.csrfmiddlewaretoken);
            },
            dataType: 'json'
        });
    }

    static get formData() {
		return $("form").serializeArray();
	}

	get query() {
		let formData = TaskBulkCreate.formData;
		let data = {};
		$(formData ).each(function(index, obj){
		    data[obj.name] = obj.value;
		});
        if (data.person_asked_by === "") {
            data.person_asked_by = String(this.defaultPersonAskedBy);
        }
        data.performance_place = this.performancePlace;
        if (!data.movement){
            data.movement = this.movement;
        }
		return data;
	}

    validateForm() {
	    this.clearFormErrors();
	    this.validatePersonCustomer();
	    this.validateTypeTask();
        this.validateLawsuit();
        this.validatePerformancePlace();
        this.validateFinalDeadlineDate();
        if (this.formErrors.length <= 0) {
            return false;
        }
        let htmlErrors = this.getErrors();
        swal({
            title: 'Campos obrigatórios não preenchidos',
            width: '45%',
            html: htmlErrors,
            type: 'error'
        });
        return this.formErrors.length;
    }

    save() {
        let formErrors = this.validateForm();
        if (!formErrors) {
            let data = this.query;
            this.submitForm(data);
        }
    }

    onSaveSubmit() {
        $('[type=submit]').on('click', (el)=> {                
            el.preventDefault();
            this.save();
        });
    }

    updateTaskStatus(action) {
	    if(this.baseURL && this.taskID && action) {
	        TaskBulkCreate.swalLoading('Aguarde...');
            $.ajax({
                type: 'POST',
                url: '/providencias/ajax_bulk_create_update_status/',
                data: {'task_id': this.taskID},
                success: (result) => {
                    window.location.replace(`${this.getActionTaskURL(action)}`);
                },
                error: (request, status, error) => {
                    swal.close();
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings) => {
                    xhr.setRequestHeader('X-CSRFToken', this.query.csrfmiddlewaretoken);
                },
                dataType: 'json'
            });
        }
    }

    delegateTask() {
	    if(this.baseURL && this.taskID) {
            this.updateTaskStatus('delegate');
        }
    }

    assignTask() {
	    if(this.baseURL && this.taskID) {
            this.updateTaskStatus('assign');
        }
    }

    static swalLoading(title='', message=''){
	    swal({
            title: title,
            html: message,
            allowOutsideClick: false,
            onOpen: () => {
                swal.showLoading();
            }
        });
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        this.elMovement.attr('disabled', true);
	        this.elTypeTask.select2({placeholder: 'Selecione...', language: 'pt-BR'});
	        this.elPersonAskedBy.select2({placeholder: 'Procurar...', language: 'pt-BR'});
        });
    }
}
