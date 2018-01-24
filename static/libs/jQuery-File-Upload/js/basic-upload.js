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
                document.getElementById("no-providence").innerHTML="";
                showToast('success', data.result.message, '', 3000, true);
                get_ecms(data.result.task_id);

                //language=HTML
                /*
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
                );*/

            }

            else{
                showToast('error', data.result.message, '', 0, false);
                $('#deleting').modal('hide');            }
        }

    });

});