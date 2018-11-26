class ServicePriceTable {
    constructor(){
        this.elOfficeNetwork = $('#id_office_network');
        this.elOfficeCorrespondent = $('#id_office_correspondent');
        this.onChangeOfficeNetwork();
        this.onChangeOfficeCorrespondent();
        this.onSaveSubmit();
    }

    static enableElement(element){
        element.removeAttr('disabled');
    }

    static disableElement(element){
        element.attr('disabled', true);
    }

    disableOfficeCorrespondent(){
        this.officeCorrespondent = '';
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
}