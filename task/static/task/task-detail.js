class TaskDetail {
    constructor(taskId, taskStatus, officeWorkAlone, pendingSurveys, pendingList, surveyCompanyRepresentative, csrfToken, billing, chargeId) {
        this.csrfToken = csrfToken;
        this.taskId = taskId;
        this.taskStatus = taskStatus;
        this.chargeId = chargeId;
        this.officeWorkAlone = (officeWorkAlone === 'True');
        this.pendingSurveys = pendingSurveys;
        this.pendingList = pendingList;
        this.surveyCompanyRepresentative=surveyCompanyRepresentative;
        this.billing = billing;
        this.expanded = false;            
        this.servicePriceTable = {};
        this._elTaskTitle = $('#task-title');
        this._elExecutionDate = $("input[name=execution_date]"); 
        this._elModalAction = $('#confirmAction');
        this._elRatingContainer = $('.rating-container');
        this._elFeedbackRating = $('#id_feedback_rating');
        this._elFeedbackComment = $('#id_feedback_comment');
        this._elModalActionButton = $('#actionButton');
        this._elModalNextText = $('#actionText');
        this._elModalHeader = $('#modalHeader');       
        this._elNotes = $('textarea[id=notes_id]');
        this._elBtnCompanyRepresentative = $('#btn-company_representative');
        this._elModalSurveyCompanyRepresentative = $("#survey-company-representative");
        this._elExecutionDate.attr({'required': true, 'placeholder': 'Data de Cumprimento'});
        this._elTypeTaskField = $('#id_type_task_field');        
        this.initFeedbackRating();
        this.initCpfCnpjField();
        this.onClickRowServicePriceTable();  
        this.checkPaymentPending();
        this.onDocumentReady();
    }

    static createListItens(listItems) {
            let htmlListItens = '';
            for (var i = 0; i < listItems.length; i++) {
                htmlListItens += `<li>${listItems[i]}</li>`;
            }
            return htmlListItens;
        }

    get servicePriceTableId(){
        let servicePriceTableId = $('input[name=servicepricetable_id]').val();
        this.setServicePriceDetail(servicePriceTableId);
        return servicePriceTableId;
    }

    set servicePriceTableId(value) {
        $('input[name=servicepricetable_id]').val(value);
    }

    get officeToDelegate() {
        return $("#office-" + this.servicePriceTableId);
    }    

    get officeToDelegateName() {
        return $(this.officeToDelegate).find('td.office_correspondent').text()
    }

    get officeToDelegateValue() {
        return this.officeToDelegate.data('value')
    }

    get nextState() {
        return {
            REQUESTED: {text: "recusar", icon: "mdi mdi-clipboard-alert"},
            ACCEPTED_SERVICE: {text: "aceitar", icon: "mdi mdi-thumb-up-outline"},
            REFUSED_SERVICE: {text: "recusar", icon: "mdi mdi-thumb-down-outline"},
            OPEN: {text: "delegar", icon: "mdi mdi-account-location"},
            ACCEPTED: {text: "aceitar", icon: "mdi mdi-calendar-clock"},
            REFUSED: {text: "recusar", icon: "mdi mdi-clipboard-alert"},
            DELEGATED: {text: "delegar", icon: "assignment_returned"},
            DONE: {text: "Cumprir", icon: "mdi mdi-checkbox-marked-circle-outline"},
            FINISHED: {text: "Finalizar", icon: "mdi mdi-gavel"},
            BLOCKEDPAYMENT: {text: "Glosar", icon: "mdi mdi-currency-usd-off"},
            RETURN: {text: "Retornar", icon: "mdi mdi-backburger"}
        };
    }

    checkPaymentPending() {
        if (this.chargeId) {
            this.billing.checkout.chargeId = this.chargeId;
            this.billing.checkout.getPaymentStatus();
        }
    }

    setServicePriceDetail(servicePriceTableId) {
        $.ajax({
            method: 'GET', 
            url: `/financeiro/tabelas-de-precos/detalhes/${servicePriceTableId}/`, 
            success: (response) => {
                this.servicePriceTable = response;
            }
        })
    }    


    setBillingItem() {
        this.billing.item =
          {
            task_id: this.taskId, 
            service_price_table_id: this.servicePriceTableId,
            name: this._elTaskTitle.text() + ' para ' + this.officeToDelegateName, 
            value: parseInt(String(this.officeToDelegate.data('value'))
                .replace('.', '')
                .replace(', ', ''))
          };         
    }

    setExecutionDateRequire(status) {
        if (this._elExecutionDate.length > 0) {
            if (status === "REQUESTED"){
                this._elExecutionDate.attr('required', false);
                this._elExecutionDate.val('');

            }else{
                this._elExecutionDate.attr('required', true);
            }
            let input = this._elExecutionDate.get(0);
            if (! input.checkValidity()) {
                input.reportValidity();
                return false;
            }
        }
    }

    showModalAction() {
        this._elModalAction.modal('show');
    }

    hideModalAction() {
        this._elModalAction.modal('hide');
    }

    showModalSurvey(el) {
        el.modal('show');
    }

    hideModalSurvey(el) {
        el.modal('hide');
    }

    validSurvey(status) {
        if(status === 'FINISHED' && this.pendingSurveys){
            let htmlList = `<ul class='font-15 text-left'>${TaskDetail.createListItens(this.pendingList)}</ul>`;
            let html = `<h4>A OS não pode ser finalizada porque o questionário do(s) participante(s) a seguir não foi 
                            respondido:</h4>
                        <br />${htmlList}`;
            swal({
                type: 'error',
                title: 'Questionário',
                html: html,
            });
        }        
    }

    showRatingContainer() {
        this._elRatingContainer.show();
    }

    hideRatingContainer() {
        this._elRatingContainer.hide();
        this._elFeedbackRating.rating('rate', '');
        this._elFeedbackComment.val('');        
    }

    makeRatingProccess(status) {
        if ((status === 'BLOCKEDPAYMENT' || status === 'FINISHED') && !(this.officeWorkAlone)) {
            this.showRatingContainer();
        } else {
            this.hideRatingContainer();
        }
    }

    configNotesField(status) {        
        /*Apenas estes status devem possuir notes como required, alem de nao poder 
         espacos em branco */        
        this._elNotes.removeAttr('required');        
        ['REQUESTED', 'REFUSED', 'BLOCKEDPAYMENT', 'RETURN', 'REFUSED_SERVICE'].forEach(function (s) {
            if (status === s) {
                this._elNotes.attr('required', true).change(function () {
                    this._elNotes.val(this._elNotes.val().trim())
                });
            }
        });
    }

    formatModalAction(status) {
        this._elModalNextText.innerHTML = this.nextState[status]['text'];
        $('#icon').addClass(this.nextState[status]['icon']);
        actionButton.innerHTML = "<i class='"+this.nextState[status]['icon']+"'></i> "+
            this.nextState[status]['text'].replace(this.nextState[status]['text'][0],
                this.nextState[status]['text'][0].toUpperCase());
        this._elModalActionButton.attr("name", "action");
        this._elModalActionButton.attr("value", status);
    }

    hideServicePriceTableAlert() {
        $("#servicepricetable-alert").addClass("hidden");
    }

    initFeedbackRating() {
        this._elFeedbackRating.hide().rating({});
    }

    makeTaskAction(value) {
        var task_status = value.id;
        this.validSurvey();
        this.makeRatingProccess(value.id);
        this.setExecutionDateRequire(value.id);
        this.showModalAction();                
        this.formatModalAction(value.id);
        this.hideServicePriceTableAlert();
        this.configNotesField();
        return true;
    }

    initCpfCnpjField() {
        [].slice.call(document.querySelectorAll('.sttabs')).forEach(function(el) {
            new CBPFWTabs(el);
        });        
    }

    onClickBtnCompanyRepresentative() {
        this._elBtnCompanyRepresentative.on('click', (event)=>{
            if(this.surveyCompanyRepresentative) {
                this.showModalSurvey(this._elModalSurveyCompanyRepresentative)
            } else {
                swal({
                    type: 'error', 
                    title: 'Questionário',
                    text: "Não existe formulário cadastrado para este tipo de serviço."
                });                
            }
        })
    }

    toogleModals(modalToClose, modalToOpen, status) {
        $(modalToClose).one('hidden.bs.modal', function() {
            $('#survey').attr('data-status', status);
            $(modalToOpen).modal('show');
        }).modal('hide');
    }

    beforeSubmit(task_status) {
        this.toogleModals('#confirmAction', '#survey', task_status);
        $('#task_detail').submit(function (e) {
            e.preventDefault();
        });
        $('#actionButton').removeAttr('disabled')
    }        

    checkDelegationOffice() {        
        $('#task_detail').submit(function (e) {
            e.preventDefault();                
        });
        if (this.servicePriceTableId === ""){
            $("#alert-correspondent").remove();
            $("#servicepricetable-alert").removeClass("hidden");
            this._elModalActionButton.removeAttr('disabled');        
        } else{
            $('<input />').attr('type', 'hidden')
                .attr('name', 'action')
                .attr('value', 'OPEN')
                .appendTo('#task_detail');
                if (this.servicePriceTable.policy_price.billing_moment === 'PRE_PAID') {
                    this.hideModalAction();
                    this.billing.createCharge(this.csrfToken)
                } else {
                    swal({
                        title: 'Delegando', 
			            html: '<h4>Aguarde...</h4>',
                        onOpen: () => {
                            swal.showLoading();
                            $('#task_detail').unbind('submit').submit();            
                        }
                    })
                }
        }        
    }

// Todo: Ajustar de desmembrar
    submitTaskDetail(actionButton, use_service) {
        let task_status = actionButton.value;
        let have_survey = actionButton.getAttribute('survey');
        let ret;
        actionButton.disabled = true;
        if ((task_status === 'DONE' || task_status === 'FINISHED' && use_service === 'False') && have_survey){
            this.beforeSubmit(task_status);
        } else if(task_status === 'OPEN'){
            this.checkDelegationOffice();
        } else{
            ret = true;
            $('#task_detail [required]').each(function(index) {
                if (!Boolean($( this ).val())){
                    actionButton.disabled = false;
                    ret = false;
                }
            });
            if (ret) {
                $('<input name="action" value="'+ task_status +'">').appendTo($('#task_detail'));
                this.toogleModals('#confirmAction', '#processing');
                $('#task_detail').unbind('submit').submit();
            }
        }
    }
    
    resetForm(el){
        el.form.reset();
        if ($('#id_feedback_rating').length > 0) {
            $('#id_feedback_rating').rating('rate', '');
        }
    }

    onChangeTypeTaskField(){
        this._elTypeTaskField.on('change', (event) => {
            ajax_get_correspondents($(this).val())        
        })
    }

    getLocation() {
        if (navigator.geolocation) {
            $('#locating').modal('show');
            navigator.geolocation.getCurrentPosition(this.showPosition, this.showError);
        } else {
            console.log("Geolocalização não é suportada pelo browser.");
        }
    }    

    showPosition(position, taskId) {
        var data = {};
        var checkpointtype = $('#GEOLOCATION').data("checkpointtype");
        data['latitude'] = position.coords.latitude;
        data['longitude'] = position.coords.longitude;        
        data['checkpointtype'] = checkpointtype;
        data['task_id'] = taskDetail.taskId;
        var url = $('#GEOLOCATION').data("url");
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function (result) {
                console.log(result);
                if (result.ok){
                    location.reload();
                    $('#locating').modal('hide');
                }else{
                    $('#locating').modal('hide');
                    showToast('error', 'Atenção', "Localização não registrada", 0, false);
                }
            },
            error: function (request, status, error) {
            },
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", taskDetail.csrfToken);
            },
            dataType: 'json'
        })        
    }

    showError(error) {
        $('#locating').modal('hide');
        var msg = '';
        switch(error.code) {
            case error.PERMISSION_DENIED:
                msg = "O usuário negou o acesso à Geolocalização.";
                break;
            case error.POSITION_UNAVAILABLE:
                msg = "Informação de localização não disponível.";
                break;
            case error.TIMEOUT:
                msg = "Tempo limite atingido para o pedido de localização.";
                break;
            case error.UNKNOWN_ERROR:
                msg = "Ocorreu um erro desconhecido.";
                break;
        }
        showToast('error', 'Atenção', msg, 0, false);
    }    

    onClickRowServicePriceTable() {
        let self = this;
        $("#correspondents-table tbody tr").on('click', function(){            
            $("#servicepricetable-alert").addClass("hidden");            
            let rowId = $(this).data('id');
            let amount = $(this).data('value').toString();
            let priceCategory = $(this).data('price-category');
            $('input[name=servicepricetable_id]').val(rowId);
            $('input[name=amount]').val(amount.replace(".", ","));
            $(this).addClass("ezl-bg-open");
            $(this).siblings().removeClass("ezl-bg-open");
            if (priceCategory === 'NETWORK'){
                $('input[name=amount]').attr("disabled", "disabled");
            } else {
                $('input[name=amount]').removeAttr("disabled");
                $('input[name=amount]').focus();
            }
            self.setBillingItem();
        });
    };    

    ajax_get_correspondents(type_task) {
        let tmplRowCorrespondent = '<tr id="office-${pk}" data-id="${pk}" ' +
                            'data-value="${value}" data-formated-value="${formated_value}" ' +
                            'data-price-category="${price_category}" ' +
                            'data-office-public="${office_public}" class="tr_select" role="row">\n' +
                '<td class="office_correspondent">${office_correspondent}</td>\n' +
                '<td class="office_correspondent">${office_network}</td>\n' +
                '<td class="court_district">${court_district}</td>\n' +
                '<td class="court_district_complement">${court_district_complement}</td>\n' +
                '<td class="state">${city}</td>\n' +
                '<td class="state">${state}</td>\n' +
                '<td class="client">${client}</td>\n' +
                '<td class="value">${value}</td>\n' +
                '<td class="office_rating">${office_rating}</td>\n' +
                '<td class="office_return_rating">${office_return_rating}</td>\n' +
            '</tr>';
        let self = this;
        $.ajax({
            type: 'GET',
            url: `/providencias/ajax_get_correspondent_table/?task=${this.taskId}&type_task=${type_task}`,
            success: function (data) {
                window.total = data.total;
                window.table_rows = data.total;
                window.type_task_id = data.type_task_id;
                $("#type_task").html(data.type_task);
                var tbody = $('#correspondents-table tbody');
                if(window.table) {
                    window.table.clear().draw();
                }
                tbody.html('');
                if (data.total > 0) {
                    $.each(data.correspondents_table, function (index, value) {
                        $.tmpl(tmplRowCorrespondent, value).appendTo(tbody)
                    });
                }
                self.correspondents_data_table();
            },
            dataType: 'json'
        });
        return;
    };    

    correspondents_data_table() {
        window.table = $('#correspondents-table').DataTable({
            paging: false,
            order: [[7, 'asc'], [8, 'desc'], [9, 'asc'], [0, 'asc']],
            dom: 'frti',
            buttons: [],
            destroy: true,
            language: {
                "url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"
            },
        });
        this._elModalActionButton.removeAttr('disabled')        
        $("#correspondents-table_filter input").focus();
        this.onClickRowServicePriceTable();
        return;
    };   

    onKeypressAmountField() {
        $('input[id=id_amount]').keypress(function(e) {
            if(e.which == 13) {
              e.preventDefault();
            }
        });
    }

    onDocumentReady(){
	    $(document).ready(()=>{
	        if(this.taskStatus === 'ACCEPTED_SERVICE') {
                let url_string = window.location.href;
                let url = new URL(url_string);
                let action = url.searchParams.get("action")
                if (action === 'delegate') {
                    $('#OPEN').click();
                }
                if (action === 'assign') {
                    $('#ASSIGN').click();
                }
            }
        });
    }

    delegateTaskPaid(gnData, intervalCheck) {
        if (gnData.status === 'paid' &&
            (this.taskStatus === 'ACCEPTED_SERVICE' || this.taskStatus === 'REQUESTED')) {
            clearInterval(intervalCheck);
            $.ajax({
                method: 'GET', 
                url: `/financeiro/tabelas-de-precos/detalhes/${gnData.custom_id}/`, 
                success: (response) => {
                    this.servicePriceTable = response;
                    console.log(response);
                    $.ajax({
                        method: 'post', 
                        url: `/providencias/${this.taskId}/batch/delegar`, 
                        data: {
                                task_id: this.taskId,
                                servicepricetable_id: response.id,   
                                amount: response.value, 
                                note: '',                               
                            },
                        success: function(response) {                
                            if (response.status === 'ok') {
                                location.reload();
                            }
                        },
                        error: function (request, status, error) {
                        },
                        beforeSend: function (xhr, settings) {
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        dataType: 'json'                        
                    })                        
                }
            })                    
        }
    }
}

