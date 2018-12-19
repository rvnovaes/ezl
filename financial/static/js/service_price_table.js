class ServicePriceTable {
    constructor(officeSessionId, policyPricesCategories){
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

    static enableElement(element){
        element.removeAttr('disabled');
    }

    static disableElement(element){
        element.attr('disabled', true);
    }

    disableOfficeCorrespondent(){
        if (this.officeCorrespondent !== this.office) {
            this.officeCorrespondent = '';
        }
        ServicePriceTable.disableElement(this.elOfficeCorrespondent);
        this.elOfficeCorrespondent.parent().removeClass('ezl-required');
    }

    disableOfficeNetwork(){
        this.officeNetwork = '';
        ServicePriceTable.disableElement(this.elOfficeNetwork);
        this.elOfficeNetwork.parent().removeClass('ezl-required');
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

    get pricePolicyCategory(){
        return (this.policyPrice) ? this.policyPricesCategories[this.policyPrice] : null;
    }

    onChangeOfficeNetwork(){
	    this.elOfficeNetwork.on('change',()=>{
            if (this.officeNetwork) {
                this.disableOfficeCorrespondent();
            } else {
                ServicePriceTable.enableElement(this.elOfficeCorrespondent);
                this.elOfficeCorrespondent.parent().addClass('ezl-required');
            }
        });
    }

    onChangeOfficeCorrespondent(){
	    this.elOfficeCorrespondent.on('change',()=>{
            if (this.officeCorrespondent) {
                this.disableOfficeNetwork();
            } else {
                ServicePriceTable.enableElement(this.elOfficeNetwork);
                this.elOfficeNetwork.parent().addClass('ezl-required');
            }
            this.validatePolicyPrice(true);
        });
    }

    onSaveSubmit() {
        $('[type=submit]').on('click', (el)=> {
            if (!(this.officeCorrespondent || this.officeNetwork)){
                el.preventDefault();
                showToast('error', 'Atenção', 'Favor selecionar um Escritório Correspondente ou uma Rede de escritórios', 0, false);
            }
            ServicePriceTable.enableElement(this.elOfficeNetwork);
            ServicePriceTable.enableElement(this.elOfficeCorrespondent);
        });
    }

    validatePolicyPrice(showAlert) {
        let officeCorrespondentId = this.elOfficeCorrespondent.val();
        let pricePolicyCategory = this.pricePolicyCategory;
        if (pricePolicyCategory === 'PUBLIC' && officeCorrespondentId !== this.officeSessionId) {
            this.elOfficeCorrespondent.val(this.officeSessionId);
            if (showAlert) {
                swal({
                    type: 'error', 
                    title: 'Atenção!', 
                    text: 'Para tipo de preço público o escritório correspondente deve ser o mesmo em que está logado.'
                });
            }
        }
        if (pricePolicyCategory === 'NETWORK'){
            this.disableOfficeCorrespondent();
        } else{
            ServicePriceTable.enableElement(this.elOfficeCorrespondent);
        }
    }

    onChangePolicyPrice() {
        this.elPolicyPrice.on('change', (event)=>{
            this.validatePolicyPrice(false);
        });
    }
}