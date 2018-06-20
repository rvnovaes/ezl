function toggle(e) {
    checkboxes = document.getElementsByName("selection");
    for (var c in checkboxes) checkboxes[c].checked = e.checked
}

// Funcao para voltar a tela anterior
// Utilizado principalmente quando clica em um botao cancelar que esta em um formulario de criacao ou edicao
// E necessario pelo fato da necessidade retornar a pagina que o usuario estava ao clicar em editar ou criar
goToBackUrl = function (default_url) {
    if (document.referrer === '') {
        window.location.href = default_url;
    } else {
        window.history.back()
    }
};
