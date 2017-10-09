// Responsavel por gerar a linha da listagem como um link para o formulario de edicao
$(document).ready(function () {
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
});
// abre linha em nova janela
$(document).ready(function () {
    $('tr[data-new-href]').each(function () {

        $(this).find('a').removeAttr('target').removeAttr('href');

        var url = $(this).attr('data-new-href');

        $(this).find('td').each(function () {


            $(this).wrapInner('<a href="' + url + '"></a>');

            $(this).each(function () {

                // console.log('this', this);

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
