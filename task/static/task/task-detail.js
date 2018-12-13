import Task from './task'

class TaskDetail extends Task {
	constructor(taskId) {
		super(taskId);
	}
}


// $(document).ready(function(){
// 	$('#id_feedback_rating').hide().rating({});
// });

// // Aparentemente valida CPF
// (function() {
//     [].slice.call(document.querySelectorAll('.sttabs')).forEach(function(el) {
//         new CBPFWTabs(el);
//     });
// })();


// // Responde o questionario do preposto
// var taskId;
// $('#btn-company_representative').on('click', function(event) {
//     event.preventDefault();
//     taskId = '{{object.pk}}';            
//     {% if survey_company_representative %} 
//         selectedSurvey = `{{survey_company_representative|safe}}`;
//         $("#survey-company-representative").modal('show');
//     {% else %}
//         swal({
//             type: 'error', 
//             title: 'Questionário',
//             text: "Não existe formulário cadastrado para este tipo de serviço."
//         });
//     {% endif %}            
// })


// // Aparentemente é o toggle do historico
// var expanded = false;

// function toggleArrowHist() {

//     if (expanded) {
//         expanded = false;
//         document.getElementById("up_hist").style.display = "none";
//         document.getElementById("down_hist").style.display = "block";
//     }
//     else {
//         expanded = true;
//         document.getElementById("up_hist").style.display = "block";
//         document.getElementById("down_hist").style.display = "none";
//     }
// }


// // Seta o campo data de cumprimento pra requerido
// $(function () {
//     $("input[name=execution_date]").attr({'required': true,
//         'placeholder': 'Data de Cumprimento'});
// });


// // Aparentemente fecha e abre modals de acao e questionario

// function toogleModals(modalToClose, modalToOpen, task_status) {
//     $(modalToClose).one('hidden.bs.modal', function() {
//         $('#survey').attr('data-status', task_status);
//         $(modalToOpen).modal('show');
//     }).modal('hide');
// }

// //Função para exibir modal do survey
// function beforeSubmit(task_status) {
//     toogleModals('#confirmAction', '#survey', task_status);
//     $('#task_detail').submit(function (e) {
//         e.preventDefault();
//     });
//     $('#actionButton').removeAttr('disabled')
// }


// //Função para verificar se foi selecionado um escritório antes de delegar
// function checkDelegationOffice() {
//     var servicepricetable_id = $('input[name=servicepricetable_id]').val();
//     var selected_office = $("#office-"+servicepricetable_id);
//     var public_office = (selected_office.data('office-public') == "True");
//     $('#task_detail').submit(function (e) {
//         e.preventDefault();                
//     });
//     if (servicepricetable_id === ""){
//         $("#alert-correspondent").remove();
//         $("#servicepricetable-alert").removeClass("hidden");
//         $('#actionButton').removeAttr('disabled')
//     } else if (public_office){
//         var text_public_office = "Para a contratação dos serviços do EZLog deve ser feita a transferência do" +
//             " valor " + selected_office.data('formated-value') + " para a conta abaixo:" +
//             "\nBanco Bradesco" +
//             "\nAgência: 2146-6" +
//             "\nConta corrente: 40930-8" +
//             "\nSílex Sistemas Ltda." +
//             "\n04.170.575-0001-03" +
//             "\nTelefone de contato: 31 2538-7869";
//         swal({
//             title: "Importante",
//             text: text_public_office,
//             type: "warning",
//             showCancelButton: true,
//             cancelButtonText: "Cancelar",
//             confirmButtonColor: "#DD6B55",
//             confirmButtonText: "Delegar",                    
//         }).then(function(result){
//             if (result.value) {
//                 $('<input />').attr('type', 'hidden')
//                     .attr('name', 'action')
//                     .attr('value', 'OPEN')
//                     .appendTo('#task_detail');
//                 swal.close();
//                 toogleModals('#confirmAction', '#procssing')
//                 $('#task_detail').unbind('submit').submit();
//             }else{
//                 $('#actionButton').removeAttr('disabled')
//             }
//         });
//     }else{
//         $('<input />').attr('type', 'hidden')
//             .attr('name', 'action')
//             .attr('value', 'OPEN')
//             .appendTo('#task_detail');
//         $('#task_detail').unbind('submit').submit();
//         toogleModals('#confirmAction', '#processing')
//     }
// }


// // Aparentemente faz o submit do task detail
// function submit_task_detail(actionButton, use_service) {
//     var task_status = actionButton.value;
//     var have_survey = actionButton.getAttribute('survey');
//     actionButton.disabled = true;
//     if ((task_status === 'DONE' || task_status === 'FINISHED' && use_service === 'False') && have_survey){
//         beforeSubmit(task_status);
//     }else if(task_status === 'OPEN'){
//         checkDelegationOffice();
//     }else{
//         ret = true;
//         $('#task_detail [required]').each(function(index) {
//             if (!Boolean($( this ).val())){
//                 actionButton.disabled = false;
//                 ret = false;
//             }
//         });
//         if (ret) {
//             $('<input name="action" value="'+ task_status +'">').appendTo($('#task_detail'));
//             toogleModals('#confirmAction', '#processing');
//             $('#task_detail').unbind('submit').submit();
//         }
//     }

// }

// // Variaveis que representao o proximo status
// var nextState = {
//     REQUESTED: {text: "recusar", icon: "mdi mdi-clipboard-alert"},
//     ACCEPTED_SERVICE: {text: "aceitar", icon: "mdi mdi-thumb-up-outline"},
//     REFUSED_SERVICE: {text: "recusar", icon: "mdi mdi-thumb-down-outline"},
//     OPEN: {text: "delegar", icon: "mdi mdi-account-location"},
//     ACCEPTED: {text: "aceitar", icon: "mdi mdi-calendar-clock"},
//     REFUSED: {text: "recusar", icon: "mdi mdi-clipboard-alert"},
//     DELEGATED: {text: "delegar", icon: "assignment_returned"},
//     DONE: {text: "Cumprir", icon: "mdi mdi-checkbox-marked-circle-outline"},
//     FINISHED: {text: "Finalizar", icon: "mdi mdi-gavel"},
//     BLOCKEDPAYMENT: {text: "Glosar", icon: "mdi mdi-currency-usd-off"},
//     RETURN: {text: "Retornar", icon: "mdi mdi-backburger"}
// };


// // Limpa formulario

// function resetForm(el){
//     el.form.reset();
//     if ($('#id_feedback_rating').length > 0) {
//         $('#id_feedback_rating').rating('rate', '');
//     }
// }


// // Funcao que invoca o action form de acordo com o status
// function getId(value) {
//     var task_status = value.id;
//     {% if custom_settings %}
//     var office_work_alone = {{ custom_settings.i_work_alone|lower }};
//     {% else %}
//     var office_work_alone = false;
//     {% endif %}

//     if(value.id === 'FINISHED' && {{ pending_survey|lower }}){
//         swal({
//             type: 'error',
//             title: 'Questionário',
//             html: "<h4>A OS não pode ser finalizada porque o preposto não respondeu o questionário.</h4>"
//         });
//         return false;
//     }

//     if ((value.id == "BLOCKEDPAYMENT" || value.id == "FINISHED") && !(office_work_alone) ){
//         $('.rating-container').show();
//     } else {
//         $('.rating-container').hide();
//         $('#id_feedback_rating').rating('rate', '');
//         $('#id_feedback_comment').val('');
//     }

//     var $input = $("input[name=execution_date]");
//     if ($input.length > 0) {
//         if (value.id === "REQUESTED"){
//             $input.attr('required', false);
//             $input.val('');

//         }else{
//             $input.attr('required', true);
//         }
//         var input = $input.get(0);
//         if (! input.checkValidity()) {
//             input.reportValidity();
//             return false
//         }
//     }

//     $('#confirmAction').modal('show');

//     $("#servicepricetable-alert").addClass("hidden");

//     var actionButton = document.getElementById("actionButton");
//     var nextText = document.getElementById("actionText");
//     var modalHeader = document.getElementById("modalHeader");
//     nextText.innerHTML = nextState[task_status]['text'];
//     $('#icon').addClass(nextState[task_status]['icon']);
//     actionButton.innerHTML = "<i class='"+nextState[task_status]['icon']+"'></i> "+
//         nextState[task_status]['text'].replace(nextState[task_status]['text'][0],
//             nextState[task_status]['text'][0].toUpperCase());

//     actionButton.setAttribute("name", "action");
//     actionButton.setAttribute("value", task_status);

//     {# Apenas estes status devem possuir notes como required, alem de nao poder #}
//     {# espacos em branco #}

//     var notes = $('textarea[id=notes_id]');
//     notes.removeAttr('required');
//     ['REQUESTED', 'REFUSED', 'BLOCKEDPAYMENT', 'RETURN', 'REFUSED_SERVICE'].forEach(function (status) {
//         if (task_status === status) {
//             notes.attr('required', true).change(function () {
//                 notes.val(notes.val().trim())
//             });
//         }
//     });

//     return true;
// }

// // Busca os correspondentes de acordo com o tipo de serviço
// $('#id_type_task_field').on('change', function () {
//     ajax_get_correspondents($(this).val())
// })


// // Pega a posicao corrente do browser, levar para outro js
// function getLocation() {
//     if (navigator.geolocation) {
//         $('#locating').modal('show');
//         navigator.geolocation.getCurrentPosition(showPosition, showError);
//     } else {
//         console.log("Geolocalização não é suportada pelo browser.");
//     }
// }


// // Mostra dados do checkin e checkout
// function showPosition(position) {
//     var data = {};
//     var checkpointtype = $('#GEOLOCATION').data("checkpointtype");
//     data['latitude'] = position.coords.latitude;
//     data['longitude'] = position.coords.longitude;
//     data['task_id'] = {{ form.instance.pk }};
//     data['checkpointtype'] = checkpointtype;
//     var url = $('#GEOLOCATION').data("url");
//     $.ajax({
//         type: 'POST',
//         url: url,
//         data: data,
//         success: function (result) {
//             console.log(result);
//             if (result.ok){
//                 location.reload();
//                 $('#locating').modal('hide');
//             }else{
//                 $('#locating').modal('hide');
//                 showToast('error', 'Atenção', "Localização não registrada", 0, false);
//             }
//         },
//         error: function (request, status, error) {
//         },
//         beforeSend: function (xhr, settings) {
//             xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
//         },
//         dataType: 'json'
//     })
// }


// // Mostra errro caso nao consiga pegar a localizacao
// function showError(error) {
//     $('#locating').modal('hide');
//     var msg = '';
//     switch(error.code) {
//         case error.PERMISSION_DENIED:
//             msg = "O usuário negou o acesso à Geolocalização.";
//             break;
//         case error.POSITION_UNAVAILABLE:
//             msg = "Informação de localização não disponível.";
//             break;
//         case error.TIMEOUT:
//             msg = "Tempo limite atingido para o pedido de localização.";
//             break;
//         case error.UNKNOWN_ERROR:
//             msg = "Ocorreu um erro desconhecido.";
//             break;
//     }
//     showToast('error', 'Atenção', msg, 0, false);
// }



// // Altera o estilo da linha selecionada na tabela de precos
// var row_click_function = function (){
//     $("#correspondents-table tbody tr").click(function(){
//         $("#servicepricetable-alert").addClass("hidden");
//         id = $(this).data('id');
//         amount = $(this).data('value').toString();
//         $('input[name=servicepricetable_id]').val(id);
//         $('input[name=amount]').val(amount.replace(".", ","));
//         $(this).addClass("ezl-bg-open");
//         $(this).siblings().removeClass("ezl-bg-open");
//         $('input[name=amount]').focus();
//     });

//     return;
// };

// // Aparentemente monta a tabela de precos
// var ajax_get_correspondents = function (type_task) {
//     var tmplRowCorrespondent = '<tr id="office-${pk}" data-id="${pk}" ' +
//                         'data-value="${value}" data-formated-value="${formated_value}" ' +
//                         'data-office-public="${office_public}" class="tr_select" role="row">\n' +
//             '<td class="office_correspondent">${office_correspondent}</td>\n' +
//             '<td class="office_correspondent">${office_network}</td>\n' +
//             '<td class="court_district">${court_district}</td>\n' +
//             '<td class="court_district_complement">${court_district_complement}</td>\n' +
//             '<td class="state">${city}</td>\n' +
//             '<td class="state">${state}</td>\n' +
//             '<td class="client">${client}</td>\n' +
//             '<td class="value">${value}</td>\n' +
//             '<td class="office_rating">${office_rating}</td>\n' +
//             '<td class="office_return_rating">${office_return_rating}</td>\n' +
//         '</tr>';
//     $.ajax({
//         type: 'GET',
//         url: '/providencias/ajax_get_correspondent_table/?task={{ form.instance.pk }}&type_task='+type_task,
//         success: function (data) {
//             window.total = data.total;
//             window.table_rows = data.total;
//             window.type_task_id = data.type_task_id;
//             $("#type_task").html(data.type_task);
//             var tbody = $('#correspondents-table tbody');
//             if(window.table) {
//                 window.table.destroy();
//             }
//             tbody.html('');
//             if (data.total > 0) {
//                 $.each(data.correspondents_table, function (index, value) {
//                     $.tmpl(tmplRowCorrespondent, value).appendTo(tbody)
//                 });
//             }
//             correspondents_data_table();
//         },
//         dataType: 'json'
//     });
//     return;
// };

// // Cria um dataTable da tabela de correspondentes
// var correspondents_data_table = function() {
//     window.table = $('#correspondents-table').DataTable({
//         paging: false,
//         order: [[7, 'asc'], [8, 'desc'], [9, 'asc'], [0, 'asc']],
//         dom: 'frti',
//         buttons: [],
//         destroy: true,
//         language: {
//             "url": "//cdn.datatables.net/plug-ins/1.10.16/i18n/Portuguese-Brasil.json"
//         },
//     });
//     $('#actionButton').removeAttr('disabled');
//     row_click_function();
//     $("#correspondents-table_filter input").focus();
//     return;
// };

// $('input[id=id_amount]').keypress(function(e) {
//     if(e.which == 13) {
//       e.preventDefault();
//     }
// });

// // Habilita botao de pagamento
// var billing;
// $gn.ready(function(obj) {
//   billing = new Billing(obj);                                          
// });