class TaskDetail {
    constructor(taskId, officeWorkAlone, pendingSurvey, surveyCompanyRepresentative, csrfToken) {
        this.csrfToken = csrfToken;
        this.taskId = taskId
        this.officeWorkAlone = officeWorkAlone;
        this.pendingSurvey = pendingSurvey;
        this.surveyCompanyRepresentative=surveyCompanyRepresentative;
        this.expanded=false;    
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

    }

    // Funcao que invoca o action form de acordo com o status

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
                return false
            }
        }
    }

    showModalAction() {
        this._elModalAction.modal('show')
    }

    hideModalAction() {
        this._elModalAction.modal('hide')
    }

    showModalSurvey(el) {
        el.modal('show')
    }

    hideModalSurvey(el) {
        el.modal('hide')
    }

    validSurvey(status) {
        if(status === 'FINISHED' && this.pendingSurvey){
            swal({
                type: 'error',
                title: 'Questionário',
                html: "<h4>A OS não pode ser finalizada porque o preposto não respondeu o questionário.</h4>"
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
        if ((status === 'BLOCKEDPAYMENT' || status == 'FINISHED') && !(this.officeWorkAlone)) {
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
        this.makeRatingProccess(value.id)
        this.setExecutionDateRequire(value.id);
        this.showModalAction();                
        this.formatModalAction(value.id)
        this.hideServicePriceTableAlert();
        this.configNotesField()
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
        toogleModals('#confirmAction', '#survey', task_status);
        $('#task_detail').submit(function (e) {
            e.preventDefault();
        });
        $('#actionButton').removeAttr('disabled')
    }        

// Todo: desmembrar
    checkDelegationOffice() {
        var servicepricetable_id = $('input[name=servicepricetable_id]').val();
        var selected_office = $("#office-"+servicepricetable_id);
        var public_office = (selected_office.data('office-public') == "True");
        $('#task_detail').submit(function (e) {
            e.preventDefault();                
        });
        if (servicepricetable_id === ""){
            $("#alert-correspondent").remove();
            $("#servicepricetable-alert").removeClass("hidden");
            $('#actionButton').removeAttr('disabled')
        } else if (public_office){
            var text_public_office = "Para a contratação dos serviços do EZLog deve ser feita a transferência do" +
                " valor " + selected_office.data('formated-value') + " para a conta abaixo:" +
                "\nBanco Bradesco" +
                "\nAgência: 2146-6" +
                "\nConta corrente: 40930-8" +
                "\nSílex Sistemas Ltda." +
                "\n04.170.575-0001-03" +
                "\nTelefone de contato: 31 2538-7869";
            swal({
                title: "Importante",
                text: text_public_office,
                type: "warning",
                showCancelButton: true,
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Delegar",                    
            }).then(function(result){
                if (result.value) {
                    $('<input />').attr('type', 'hidden')
                        .attr('name', 'action')
                        .attr('value', 'OPEN')
                        .appendTo('#task_detail');
                    swal.close();
                    toogleModals('#confirmAction', '#procssing')
                    $('#task_detail').unbind('submit').submit();
                }else{
                    $('#actionButton').removeAttr('disabled')
                }
            });
        }else{
            $('<input />').attr('type', 'hidden')
                .attr('name', 'action')
                .attr('value', 'OPEN')
                .appendTo('#task_detail');
            $('#task_detail').unbind('submit').submit();
            toogleModals('#confirmAction', '#processing')
        }        
    }

// Todo: Ajustar de desmembrar
    submitTaskDetail(actionButton, use_service) {
        let task_status = actionButton.value;
        let have_survey = actionButton.getAttribute('survey');
        let ret;
        actionButton.disabled = true;
        if ((task_status === 'DONE' || task_status === 'FINISHED' && use_service === 'False') && have_survey){
            beforeSubmit(task_status);
        }else if(task_status === 'OPEN'){
            checkDelegationOffice();
        }else{
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

    // Verificar a nescessidade
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

    row_click_function() {
        $("#correspondents-table tbody tr").click(function(){
            $("#servicepricetable-alert").addClass("hidden");
            id = $(this).data('id');
            amount = $(this).data('value').toString();
            $('input[name=servicepricetable_id]').val(id);
            $('input[name=amount]').val(amount.replace(".", ","));
            $(this).addClass("ezl-bg-open");
            $(this).siblings().removeClass("ezl-bg-open");
            $('input[name=amount]').focus();
        });

        return;
    };    

    ajax_get_correspondents(type_task) {
        var tmplRowCorrespondent = '<tr id="office-${pk}" data-id="${pk}" ' +
                            'data-value="${value}" data-formated-value="${formated_value}" ' +
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
        $.ajax({
            type: 'GET',
            url: '/providencias/ajax_get_correspondent_table/?task={{ form.instance.pk }}&type_task='+type_task,
            success: function (data) {
                window.total = data.total;
                window.table_rows = data.total;
                window.type_task_id = data.type_task_id;
                $("#type_task").html(data.type_task);
                var tbody = $('#correspondents-table tbody');
                if(window.table) {
                    window.table.destroy();
                }
                tbody.html('');
                if (data.total > 0) {
                    $.each(data.correspondents_table, function (index, value) {
                        $.tmpl(tmplRowCorrespondent, value).appendTo(tbody)
                    });
                }
                correspondents_data_table();
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
        $('#actionButton').removeAttr('disabled');
        this.row_click_function();
        $("#correspondents-table_filter input").focus();
        return;
    };   

    onKeypressAmountField() {
        $('input[id=id_amount]').keypress(function(e) {
            if(e.which == 13) {
              e.preventDefault();
            }
        });
    }     
}

