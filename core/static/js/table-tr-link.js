// Responsavel por gerar a linha da listagem como um link para o formulario de edicao
function addLinkOnRows(){
    $('tr[data-href]').each(function () {
        $(this).find('a').removeAttr('target').removeAttr('href');
        var $url = $(this).attr('data-href');
        $(this).find('td').each(function () {
            $(this).each(function () {
                if ($(this).attr('class') !== 'selection') {
                    if ($url.length > 0) {
                        $(this).on('click', function () {
                            window.location.href = $url;
                            window.open(
                                $url,
                                '_self'
                            )
                        })
                    }
                }
            })
        })
    });
}

function removeLinkFromRows(){
    $('tr[data-href] td').each(function () {
        $(this).off('click');
    });
}

$(document).ready(function () {
    addLinkOnRows();
});

// abre linha em nova janela
$(document).ready(function () {
    $('tr[data-new-href]').each(function () {

        $(this).find('a').removeAttr('target').removeAttr('href');

        var url = $(this).attr('data-new-href');

        $(this).find('td').each(function () {

            $(this).each(function () {

                if ($(this).attr('class') !== 'selection') {
                    if (url.length > 0) {
                        $(this).on('click', function () {
                            window.open(
                                url,
                                '_blank'
                            )
                        })
                    }
                }


            })
        })
    });
});
