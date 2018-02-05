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
                swal("Sucesso", data.result.message, "success")
                get_ecms(data.result.task_id);
            } else {
                swal('Erro', data.result.message, 'error');
            }
        }

    });

});