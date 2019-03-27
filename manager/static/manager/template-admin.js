class TemplateAdmin {
    constructor(jsonEditor, elJsonEditor) {
        this._elType = $('#id_type');
        this._elJsonEditor = (elJsonEditor);
        this.jsonEditor = jsonEditor;
        this.options = this.jsonEditor.options;
        this.ontypeChange();
    }

    get type() {
        return this._elType.val();
    }

    get initial(){
        let initialValues = this.jsonEditor.getValue();
        switch (this.type) {
            case 'BOOLEAN':
                TemplateAdmin.removeFromObj(initialValues, 'foreign_key_default');
                break;
            case 'FOREIGN_KEY':
                TemplateAdmin.removeFromObj(initialValues, 'boolean_default');
                break;
        }
        return this.jsonEditor.getValue();
    }

    static removeFromObj(obj, objItem){
        if (obj.hasOwnProperty(objItem)){
            delete obj[objItem];
        }
    }

    createJsonEditor(){
        this.jsonEditor = new JSONEditor(this._elJsonEditor, this.options);
    }

    getRequiredList(){
        let requiredList = ["is_required"];
        switch (this.type) {
            case 'BOOLEAN':
                requiredList.push("boolean_default");
                break;
            case 'FOREIGN_KEY':
                requiredList.push("foreign_key_default");
                break;
        }
        return requiredList;
    }

    changeRequired(requiredList){
        this.options.schema.required = requiredList;
    }

    ontypeChange(){
        this._elType.on('change', () => {
            let requiredList = this.getRequiredList();
            this.changeRequired(requiredList);
            let initial = this.initial;
            this.jsonEditor.destroy();
            this.createJsonEditor();
            this.jsonEditor.setValue(initial);
            this.onChangeJsonEditor();
            parameters_editor = this.jsonEditor;
        });
    }

    onChangeJsonEditor(){
        this.jsonEditor.on('change', () => {
            var errors = this.jsonEditor.validate();
            if (errors.length) {
                console.log(errors);
            }
            else {
                var json = this.jsonEditor.getValue();
                document.getElementById("id_parameters").value = JSON.stringify(json);
            }
        });
    }
}