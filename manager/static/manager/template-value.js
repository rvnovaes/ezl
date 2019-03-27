class TemplateValue {
    constructor() {
        this.officeTemplateValue = {};
        this.templateValuesTable = null;
        this._elFormOfficeConfig = $('#form-office-config');
        this._elTemplateValuesTable = $('#template-values-table');
        this._elBtnSave = $('#btn-save');
        this.onSaveSubmit();
        this.onDocumentReady();
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

    static getInputElement(type, name){
        let inputElementObj = {
            type: type,
            name: name
        };
        return $('<input>', inputElementObj);
    }

    async getForeignKeySelect(parameters, name, value=null){
        let data = parameters.foreign_key_default[0];
        window.dados = data;
        let foreignKeyData = {};
        foreignKeyData = await this.ajaxGetForeignKeyData(data);
        let select = $('<select></select>')
            .attr('name', name)
            .addClass('select2')
            .attr('data-language', 'pt-BR')
            .attr('data-placeholder', 'Procurar...');
        select.append($('<option></option>').attr('value', null).text('Escolha uma opção'));
        $.each(foreignKeyData.values,(index,option) => {
            let selected = '';
            if (parseInt(value) === option.id){
                selected = 'selected';
            }
            select.append($(`<option ${selected}></option>`).attr('value', option.id).text(option.text_select));
        });
        return select;
    }

    async getTableField(id, type, parameters, value){
        let isRequired = parameters.is_required;
        let element = $('<div class="form-group col-sm-12"></div>');
        let inputElement = null;
        let elementName = `template-value-${id}`;
        switch (type) {
            case 'SIMPLE_TEXT':
                inputElement = TemplateValue.getInputElement('text', elementName);
                inputElement.val(value);
                break;
            case 'LONG_TEXT':
                inputElement = $(`<textarea name="template-value-${id}">${value}</textarea>`);
                break;
            case 'BOOLEAN':
                inputElement = TemplateValue.getInputElement('checkbox', elementName);
                if(value === 'on'){
                    inputElement.attr('checked', true);
                }
                break;
            case 'INTEGER':
                inputElement = TemplateValue.getInputElement('number', elementName);
                inputElement.val(value);
                break;
            case 'DECIMAL':
                inputElement = TemplateValue.getInputElement('number', elementName);
                inputElement.val(value);
                inputElement.attr('step', '0.1');
                break;
            case 'FOREIGN_KEY':
                inputElement = await this.getForeignKeySelect(parameters, elementName, value);
                break;

        }
        if (isRequired && inputElement) {
            element.addClass('ezl-required');
            inputElement.prop('required', true);
        }
        element.append(inputElement);
        return element[0].outerHTML;
    }

    get formData() {
		return this._elFormOfficeConfig.serializeArray();
	}


	async ajaxGetForeignKeyData (data){
        try {
            return await $.ajax({
                type: 'GET',
                url: '/configuracoes/get_foreign_key_data/',
                dataType: 'json',
                data: data,
            });
        } catch (e) {
            console.log(e);
            throw e;
        }
    }

    async ajaxGetOfficeTemplateValues (){
        return await $.ajax({
            type: 'GET',
            url: '/configuracoes/get_office_template_value/',
            dataType: 'json'
        });
    }

    async createDataTable(){
        return await this._elTemplateValuesTable
            .DataTable({
                destroy: true,
                paging: false,
                order: [[1, 'asc']],
                dom: 'frti',
                language: {'url': '//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json'},
                columnDefs: [
                    {'targets': [0], 'visible': false, 'searchable': false, 'orderable': false  },
                    {'targets': [3], 'visible': true, 'searchable': false, 'orderable': false  },
                ],
            });
    }

    addDataTableRows(){
        if (this.officeTemplateValue.template_values.length > 0){
            this.officeTemplateValue.template_values.forEach(async (row) => {
                let rowId = row.id;
                let templateName = row.template__name;
                let templateDescription = row.template__description;
                let templateParameters = row.template__parameters;
                let templateType = row.template__type;
                let rowValue  = row.value.value || '';
                let value = await this.getTableField(rowId, templateType, templateParameters, rowValue);
                let templateRow = this.templateValuesTable.row.add(
                    [
                        rowId,
                        templateName,
                        templateDescription,
                        value
                    ]
                ).node();
                this.templateValuesTable.draw(false);
            });
        }
        return 'teste'
    }

	async createTemplateValueTable(){
        this.officeTemplateValue = await this.ajaxGetOfficeTemplateValues();

        if (!this.templateValuesTable) {
            this.templateValuesTable = await this.createDataTable();
        }
        await this.addDataTableRows();

        return true;
    }

    checkFormValidity(){
        this._elFormOfficeConfig.removeClass('validateDontSubmit');
        return this._elFormOfficeConfig[0].checkValidity();
    }

    onSaveSubmit() {
        this._elBtnSave.on('click', (el) => {
            if(! this.checkFormValidity()){
                this._elFormOfficeConfig.addClass('validateDontSubmit');
                $('<input type="submit">').hide().appendTo(this._elFormOfficeConfig).click().remove();
                return false;
            }
            TemplateValue.swalLoading('Aguarde');
            let data = this.formData;
            $.ajax({
                type: 'POST',
                url: window.location,
                data: data,
                success: (result) => {
                    swal.close();
                },
                error: (request, status, error) => {
                    swal.close();
                    showToast('error', 'Atenção', error, 0, false);
                },
                beforeSend: (xhr, settings) => {
                    xhr.setRequestHeader('X-CSRFToken', data.csrfmiddlewaretoken);
                },
                dataType: 'json'
            });
        });
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        this.createTemplateValueTable()
	        setTimeout(function () {
                $('.select2').select2();
            }, 400);
        });
    }
}