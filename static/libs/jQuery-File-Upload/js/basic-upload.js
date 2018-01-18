SurveyUploadDatabase  = {
    currentField: null
}

FileUploadSettings = {
    dataType: 'json',
    //Envia os arquivos um-a-um
    sequentialUploads: false,

    // Mostra a janela modal com progress bar ao início do upload
    start: function (e) {
        $("#modal-progress").modal("show");
    },

    // Depois de enviado o(s) arquivo(s), encerra a janela modal
    stop: function (e) {
        $("#modal-progress").modal("hide");
    },

    // Atualiza o Progress bar de acordo com o andamento do envio do arquivo
    progressall: function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        var strProgress = progress + "%";
        $(".progress-bar").css({"width": strProgress});
        $(".progress-bar").text(strProgress);
    },
    done: function (e, data) {
        if (data.result.success) {
            if ($('#survey').is(':visible')) {
                $.each(survey.getAllQuestions(), function(i, question){
                    if (question.id == SurveyUploadDatabase.currentField) {
                        question.isRequired = false;
                        $input_container = $('#' + question.id).parent();
                        $input_container.find('.upload-done').remove();
                        $label = $('<div class="upload-done alert alert-success"><strong>' + data.result.filename + '</strong> adicionado à providência.</div>');
                        $input_container.append($label);
                        $input_container.find('.alert-danger').remove();
                    }
                });
            } else {
                SurveyUploadDatabase.currentField = null;
            }

            document.getElementById("no-providence").innerHTML="";
            showToast('success', data.result.message, '', 3000, true);
            $("#files tbody").prepend(
                "<tr class='lineFile' id='row-"+ data.result.id +"'>" +
                    "<td id='cell-table'>" +
                        "<div class='row' id='row-file'>" +
                            "<div class='col-sm-2' style='text-align: center !important; vertical-align: middle !important;'>" +
                                "<i class='material-icons'>person_pin</i>" +
                            "</div>" +
                            "<div class='col-sm-8' style='text-align: left; padding-left: 0;'>" +
                                "<h6 style='margin-bottom: 3px !important;'>" + data.result.username + " (" + data.result.user + ")" +
                                "</h6>" +
                                "<div style='font-size: x-small'>" +
                                     moment().tz("America/Sao_Paulo").format("DD [de] MMMM [de] YYYY [às] HH:mm") +
                                "</div>" +
                            "</div>" +
                        "</div>" +
                    "</td>" +
                    "<td id='cell-table' style='font-size: small; width: 70% !important;'>" +
                        "<a href='/media/ECM/"+ data.result.task_id + '/' +data.result.filename +"' download " +
                        "style='text-decoration: none;'>"+ data.result.filename +"</a>" +
                    "</td>" +
                    "<td id='cell-table' style='font-size: small'>" +
                        "<i class='material-icons' id='' style='cursor: pointer; font-size: medium;'" +
                        "data-toggle='modal'" +
                        "data-target='#confirmDelete-"+ data.result.id +"'>delete</i>" +
                    "</td>" +
                "</tr>" +
                "<tr class='spaceFile' id='row-space"+ data.result.id +"'></tr>"
            );

            $("#modals").prepend(
                "<div id='confirmDelete-" + data.result.id + "' class='modal'>" +
                    "<div class='modal-dialog'>" +
                        "<div class='modal-content '>" +
                            "<div class='modal-body' style='text-align: center !important;'>" +
                                "Tem certeza que deseja excluir o arquivo <b>" + data.result.filename + "</b> ?" +
                            "</div>" +
                            "<div class='modal-footer'>" +
                                "<div class='form-group text-center'>" +
                                    "<button type='button' style='width: 95px!important;'" +
                                        "class='btn btn-sm btn-raised btn-default'" +
                                        "data-dismiss='modal'>" +
                                        "Não" +
                                    "</button>" +
                                    "<button value='1' id='delete-ecm-" + data.result.id + "'" +
                                        "style='width: 95px!important;'" +
                                        "class='btn btn-sm btn-raised btn-primary'" +
                                        "data-dismiss='modal'>Sim" +
                                    "</button>" +
                                "</div>" +
                            "</div>" +
                        "</div>" +
                    "</div>" +
                "</div>"
            );

            //language=HTML
            $("#scripts").prepend(
                "<script>"+
                "$('#delete-ecm-"+ data.result.id +"').click(function () {" +
                        "$('#deleting').modal('show');" +
                        "$.ajax({" +
                            "url: '/providencias/ecm/"+ data.result.id +"/excluir'," +
                            "dataType: 'json'," +

                            "success: function (data) {" +
                                "if (data.is_deleted) {" +
                                    "showToast('success', data.message, '', 3000, true);" +
                                    "$('#row-"+ data.result.id +"').remove();" +
                                    "$('#row-space"+ data.result.id +"').remove();" +
                                    "$('#deleting').modal('hide');" +
                                "}" +
                                "else {" +
                                    "showToast('error', data.message, '', 0, false);" +
                                    "$('#deleting').modal('hide');" +
                                "}" +

                                "if (data.num_ged == 0) {" +
                                    "document.getElementById('no-providence').innerHTML = 'Esta providência não possui nenhum arquivo em anexo.';"+

                                "}" +
                            "}" +
                        "})" +
                    "}" +
                ");"+
                "</script>"
            );

        }

        else{
            showToast('error', data.result.message, '', 0, false);
            $('#deleting').modal('hide');            }
    }
};

$(function () {

    $(".js-upload-files").click(function () {
        $("#fileupload").click();
    });

    $("#fileupload").fileupload(FileUploadSettings);

});