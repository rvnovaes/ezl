SurveyUploadDatabase  = {
    currentField: null
};
$(document).ready(function() {
    $(function () {
        $(".js-upload-files").click(function () {
            $("#fileupload").click();
        });

        $("#fileupload").fileupload({
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
                        $.each(survey.getAllQuestions(), function (i, question) {
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
                } else {
                    swal('Erro', data.result.message, 'error');
                }
            }

        });

    });
});