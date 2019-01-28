class ServicePriceTable {
    constructor(officeSessionId, policyPricesCategories){
        this.formErrors = [];
        this.officeSessionId = officeSessionId;
        this.policyPricesCategories = policyPricesCategories;
        this.elOfficeNetwork = $('#id_office_network');
        this.elOfficeCorrespondent = $('#id_office_correspondent');
        this.elOffice = $('#id_office');
        this.elPolicyPrice = $('select[name=policy_price]');
        this.onChangeOfficeNetwork();
        this.onChangeOfficeCorrespondent();
        this.onSaveSubmit();
        this.onChangePolicyPrice();
    }

    static showSwal(type, title, html){
        swal({
            type: type,
            title: title,
            html: `<h4>${html}</h4>`
        });
    }

    static formatError(message){
	    return `<li>${message}</li>`;
    }

    static disableSelecElement(element, optionValue){
        $(`${element.selector} option[value=${optionValue}]`)
            .attr('disabled', 'disabled').addClass('text-muted');
    }

    static enableSelecElement(element, optionValue){
        $(`${element.selector} option[value=${optionValue}]`)
            .removeAttr('disabled').removeClass('text-muted');
    }

    static enableRequired(element){
        element.parent().addClass('ezl-required');
    }

    static disableRequired(element){
        element.parent().removeClass('ezl-required');
    }

    static enableElement(element){
        element.removeAttr('disabled');
    }

    static disableElement(element){
        element.attr('disabled', true);
    }

    clearFormErrors(){
	    this.formErrors.splice(0, this.formErrors.length);
    }

    insertFormErrors(error){
        this.formErrors.push(error);
    }

    getErrors(){
	    let liErrors = ``;
        this.formErrors.forEach((error) => {
            liErrors += ServicePriceTable.formatError(error);
        });
        return `
            <ul style="text-align: left;">
            ${liErrors}
            </ul>
        `;
    }

    disableOfficeCorrespondent(){
        if (this.officeCorrespondent !== this.office) {
            this.officeCorrespondent = '';
        }
        ServicePriceTable.disableElement(this.elOfficeCorrespondent);
        ServicePriceTable.disableRequired(this.elOfficeCorrespondent);
    }

    disableOfficeNetwork(){
        this.officeNetwork = '';
        ServicePriceTable.disableElement(this.elOfficeNetwork);
        ServicePriceTable.disableRequired(this.elOfficeNetwork);
    }

    disablePolicyPriceOptionsByCategory(category){
        for (let key in this.policyPricesCategories) {
            if (!this.policyPricesCategories.hasOwnProperty(key)) {continue;}
            if(this.policyPricesCategories[key] !== category){
                ServicePriceTable.disableSelecElement(this.elPolicyPrice, key);
            } else {
                ServicePriceTable.enableSelecElement(this.elPolicyPrice, key);
            }
        }
    }

    enablePolicyPriceOptions(){
        for (let key in this.policyPricesCategories) {
            if (!this.policyPricesCategories.hasOwnProperty(key)) {continue;}
            ServicePriceTable.enableSelecElement(this.elPolicyPrice, key);
        }
    }

    get officeNetwork(){
        return this.elOfficeNetwork.val();
    }

    set officeNetwork(value){
        this.elOfficeNetwork.val(value);
    }

    get officeCorrespondent(){
        return this.elOfficeCorrespondent.val();
    }

    set officeCorrespondent(value){
        this.elOfficeCorrespondent.val(value);
    }

    get office(){
        return this.elOffice.val();
    }

    get policyPrice(){
        return this.elPolicyPrice.val();
    }

    set policyPrice(value){
        return this.elPolicyPrice.val(value);
    }

    get pricePolicyCategory(){
        return (this.policyPrice) ? this.policyPricesCategories[this.policyPrice] : null;
    }

    onChangeOfficeNetwork(){
	    this.elOfficeNetwork.on('change',()=>{
            if (this.officeNetwork) {
                this.disableOfficeCorrespondent();
                this.disablePolicyPriceOptionsByCategory('NETWORK');
            } else {
                ServicePriceTable.enableElement(this.elOfficeCorrespondent);
                ServicePriceTable.enableRequired(this.elOfficeCorrespondent);
                this.enablePolicyPriceOptions();
            }
        });
    }

    onChangeOfficeCorrespondent(){
	    this.elOfficeCorrespondent.on('change',()=>{
            if (this.officeCorrespondent) {
                this.disableOfficeNetwork();
            } else {
                ServicePriceTable.enableElement(this.elOfficeNetwork);
                ServicePriceTable.enableRequired(this.elOfficeNetwork);
            }
            this.validatePolicyPrice(false);
        });
    }

    onChangePolicyPrice() {
        this.elPolicyPrice.on('change', (event)=>{
            this.validatePolicyPrice(false);
        });
    }

    onSaveSubmit() {
        $('[type=submit]').on('click', (el)=> {
            this.validatePolicyPrice(false);
            if (this.formErrors.length > 0){
                el.preventDefault();
                let errorsHTML = this.getErrors();
                ServicePriceTable.showSwal('error', 'Atenção!', errorsHTML);
            }
            ServicePriceTable.enableElement(this.elOfficeNetwork);
            ServicePriceTable.enableElement(this.elOfficeCorrespondent);
        });
    }

    validatePolicyPrice(showAlert) {
        let pricePolicyCategory = this.pricePolicyCategory;
        let errorMsg = '';
        this.clearFormErrors();
        ServicePriceTable.enableSelecElement(this.elOfficeCorrespondent, this.officeSessionId);
        switch (pricePolicyCategory) {
            case 'PUBLIC':
                this.officeCorrespondent = this.officeSessionId;
                this.disableOfficeCorrespondent();
                this.disableOfficeNetwork();
                break;
            case 'NETWORK':
                this.officeCorrespondent = '';
                this.disableOfficeCorrespondent();
                ServicePriceTable.enableElement(this.elOfficeNetwork);
                ServicePriceTable.enableRequired(this.elOfficeNetwork);
                if (!this.officeNetwork) {
                    errorMsg = 'Para tipo de preço rede é obrigatório o preenchimento da rede de escritórios.';
                    this.insertFormErrors(errorMsg);
                }
                break;
            case 'DEFAULT':
                ServicePriceTable.enableElement(this.elOfficeCorrespondent);
                ServicePriceTable.enableRequired(this.elOfficeCorrespondent);
                if(this.officeCorrespondent == this.officeSessionId){
                    errorMsg = 'Para tipo de preço padrão o escritório correspondente não pode ser o mesmo escritório atual.';
                    this.insertFormErrors(errorMsg);
                    this.officeCorrespondent = '';
                }
                if(this.officeCorrespondent == ''){
                    errorMsg = 'Para tipo de preço padrão é obrigatória a escolha de um Escritório correspondente.';
                    this.insertFormErrors(errorMsg);
                }
                ServicePriceTable.disableSelecElement(this.elOfficeCorrespondent, this.officeSessionId);
                this.disableOfficeNetwork();
                break;
            default:
                this.policyPrice = '';
                this.officeCorrespondent = '';
                this.officeNetwork = '';
                ServicePriceTable.enableElement(this.elOfficeNetwork);
                ServicePriceTable.enableRequired(this.elOfficeNetwork);
                ServicePriceTable.enableElement(this.elOfficeCorrespondent);
                ServicePriceTable.enableRequired(this.elOfficeCorrespondent);
        }
        if (!this.policyPrice){
            this.insertFormErrors('Favor selecionar um Tipo de preço');
        }
        if (!(this.officeCorrespondent || this.officeNetwork) && this.policyPrice === ''){
            this.insertFormErrors('Favor selecionar um Escritório Correspondente ou uma Rede de escritórios');
        }
        if (showAlert && this.formErrors.length > 0){
            let errorsHTML = this.getErrors();
            ServicePriceTable.showSwal('error', 'Atenção!', errorsHTML);
        }
    }
}