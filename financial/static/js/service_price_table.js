class ServicePriceTable {
    constructor(officeSessionId, policyPrices){
        this.minValue = 500;
        this.formErrors = [];
        this.officeSessionId = officeSessionId;
        this.policyPrices = policyPrices;
        this.elOfficeNetwork = $('#id_office_network');
        this.elOfficeCorrespondent = $('#id_office_correspondent');
        this.elOffice = $('#id_office');
        this.elPolicyPrice = $('select[name=policy_price]');
        this.elTaskValue = $('#id_value');
        this.elTaskValueToPay = $('#id_value_to_pay');
        this.elTaskValueToReceive = $('#id_value_to_receive');
        this.elRateCommissionRequestor = $('#id_rate_commission_requestor');
        this.elRateCommissionCorrespondent = $('#id_rate_commission_correspondent');
        this.elRateTypeReceive = $('#id_rate_type_receive');
        this.elRateTypePay = $('#id_rate_type_pay');
        this.onChangeOfficeNetwork();
        this.onChangeOfficeCorrespondent();
        this.onSaveSubmit();
        this.onChangePolicyPrice();
        this.calculateComissionValues();
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

    checkMinValue() {
        if(isNaN(parseInt(this.taskValue.replace(',', '').replace('.', '')))){
            return false;
        }
        return parseInt(this.taskValue.replace(',', '').replace('.', '')) >= this.minValue;
    }

    formatedMinValue(){
        let strMinValue = String(this.minValue)
        return `R$ ${strMinValue.substr(0, strMinValue.length - 2)},${strMinValue.substr(strMinValue.length - 2)}`;
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
        for (let key in this.policyPrices) {
            if (!this.policyPrices.hasOwnProperty(key)) {continue;}
            if(this.policyPrices[key].category !== category){
                ServicePriceTable.disableSelecElement(this.elPolicyPrice, key);
            } else {
                ServicePriceTable.enableSelecElement(this.elPolicyPrice, key);
            }
        }
    }

    enablePolicyPriceOptions(){
        for (let key in this.policyPrices) {
            if (!this.policyPrices.hasOwnProperty(key)) {continue;}
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

    get taskValue(){
        return this.elTaskValue.val();
    }

    set taskValue(value){
        return this.elTaskValue.val(value);
    }

    get taskValueToPay(){
        return this.elTaskValueToPay.val();
    }

    set taskValueToPay(value){
        return this.elTaskValueToPay.val(value);
    }

    get taskValueToReceive(){
        return this.elTaskValueToReceive.val();
    }

    set taskValueToReceive(value){
        return this.elTaskValueToReceive.val(value);
    }

    get rateCommissionRequestor(){
        return this.elRateCommissionRequestor.val();
    }

    set rateCommissionRequestor(value){
        return this.elRateCommissionRequestor.val(value);
    }

    get rateCommissionCorrespondent(){
        return this.elRateCommissionCorrespondent.val();
    }

    set rateCommissionCorrespondent(value){
        return this.elRateCommissionCorrespondent.val(value);
    }

    get rateTypePay(){
        return this.elRateTypePay.val();
    }

    set rateTypePay(value){
        return this.elRateTypePay.val(value);
    }

    get rateTypeReceive(){
        return this.elRateTypeReceive.val();
    }

    set rateTypeReceive(value){
        return this.elRateTypeReceive.val(value);
    }

    get pricePolicyCategory(){
        return (this.policyPrice) ? this.policyPrices[this.policyPrice].category : null;
    }

    get priceBillingMoment(){
        return (this.policyPrice) ? this.policyPrices[this.policyPrice].billing_moment : null;
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
            this.checkValues();
            this.validatePolicyPrice(false);
            if (this.formErrors.length > 0){
                el.preventDefault();
                let errorsHTML = this.getErrors();
                ServicePriceTable.showSwal('error', 'Atenção!', errorsHTML);
            }
            ServicePriceTable.enableElement(this.elOfficeNetwork);
            ServicePriceTable.enableElement(this.elOfficeCorrespondent);

            this.calculateComissionValues();
        });
    }

    checkValues(){
        if (this.taskValue === ''){
            this.taskValue = '0,00';
        }
        if (this.taskValueToReceive === ''){
            this.taskValueToReceive = '0,00';
        }
        if (this.taskValueToPay === ''){
            this.taskValueToPay = '0,00';
        }
        // se nao informou os valores com comissao, considera que nao tem comissao
        if (this.taskValueToPay === '0,00'){
            this.taskValueToPay = this.taskValue;
        }
        if (this.taskValueToReceive === '0,00'){
            this.taskValueToReceive = this.taskValue;
        }
        if (this.rateCommissionRequestor === ''){
            this.rateCommissionRequestor = '0,00';
        }
        if (this.rateCommissionCorrespondent === ''){
            this.rateCommissionCorrespondent = '0,00';
        }
    }

    calculateComissionValues(){
        var taskValue = this.taskValue;
        taskValue = taskValue.replace(".", "");
        taskValue = taskValue.replace(",",".");
        taskValue = parseFloat(taskValue);

        var rateCommissionCorrespondent = this.rateCommissionCorrespondent;
        rateCommissionCorrespondent = rateCommissionCorrespondent.replace(".", "");
        rateCommissionCorrespondent = rateCommissionCorrespondent.replace(",",".");
        rateCommissionCorrespondent = parseFloat(rateCommissionCorrespondent);

        var rateCommissionRequestor = this.rateCommissionRequestor;
        rateCommissionRequestor = rateCommissionRequestor.replace(".", "");
        rateCommissionRequestor = rateCommissionRequestor.replace(",",".");
        rateCommissionRequestor = parseFloat(rateCommissionRequestor);

        if (this.rateTypePay === 'PERCENT'){
            this.taskValueToPay = taskValue - taskValue * rateCommissionCorrespondent;
        } else {
            this.taskValueToPay = taskValue - rateCommissionCorrespondent;
        }

        if (this.rateTypeReceive === 'PERCENT'){
            this.taskValueToReceive = taskValue - taskValue * rateCommissionRequestor;
        } else {
            this.taskValueToReceive = taskValue - rateCommissionRequestor;
        }
    }

    validatePolicyPrice(showAlert) {
        let pricePolicyCategory = this.pricePolicyCategory;
        let pricePolicyBillingMoment = this.priceBillingMoment;
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
        if(pricePolicyBillingMoment === 'PRE_PAID' && !this.checkMinValue()){
            this.insertFormErrors(`O valor mínimo para o tipo de preço pré-pago é ${this.formatedMinValue()}`);
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