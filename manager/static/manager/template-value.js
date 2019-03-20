class TemplateValue {
    constructor() {
        this.officeTemplateValue = {};
        this.templateValuesTable = null;
        this._templateValuesTable = $('#template-values-table');

        this.onDocumentReady();
    }

    static getInputElement(type, name){
        let inputElementObj = {
            type: type,
            name: name
        };
        return $('<input>', inputElementObj);
    }

    static getTableField(id, type, parameters, value){
        let isRequired = parameters.is_required;
        let element = $('<div class="form-group col-sm-12"></div>');
        let inputElement = null;
        let elementName = `template-value-${id}`;
        switch (type) {
            case 'SIMPLE_TEXT':
                inputElement = this.getInputElement('text', elementName);
                inputElement.val(value);
                break;
            case 'LONG_TEXT':
                inputElement = $(`<textarea name="template-value-${id}">${value}</textarea>`);
                break;
            case 'BOOLEAN':
                inputElement = this.getInputElement('checkbox', elementName);
                if(value === 'true'){
                    inputElement.attr('checked', true);
                }
                break;
            case 'INTEGER':
                inputElement = this.getInputElement('number', elementName);
                inputElement.val(value);
                break;
            case 'DECIMAL':
                inputElement = this.getInputElement('number', elementName);
                inputElement.val(value);
                inputElement.attr('step', '0.1');
                break;

        }
        if (isRequired && inputElement) {
            element.addClass('ezl-required');
            inputElement.prop('required', true);
        }
        element.append(inputElement);
        return element[0].outerHTML;
    }

    async ajaxGetOfficeTemplateValues (){
        return await $.ajax({
            type: 'GET',
            url: '/configuracoes/get_office_template_value/',
            dataType: 'json'
        });
    }

    async createDataTable(){
        return await this._templateValuesTable
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
            this.officeTemplateValue.template_values.forEach((row) => {
                let rowId = row.id;
                let templateName = row.template__name;
                let templateDescription = row.template__description;
                let templateParameters = row.template__parameters;
                let templateType = row.template__type;
                let value = TemplateValue.getTableField(rowId, templateType, templateParameters, row.value);
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
    }

	async createTemplateValueTable(){
        this.officeTemplateValue = await this.ajaxGetOfficeTemplateValues();

        if (!this.templateValuesTable) {
            this.templateValuesTable = await this.createDataTable();
        }

        this.addDataTableRows();

        return true;
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        this.createTemplateValueTable();
        });
    }
}