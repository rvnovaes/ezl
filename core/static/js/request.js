var tmplRequestPersonListItem = '<li>\n' +
    '<a href="/start/"><i class="mdi mdi-account"></i> A pessoa ${person} <br /> ' +
    'deseja se vincular ao escritório ${office} &nbsp; <i class="fa fa-angle-right"></i>' +
    '</li>\n';

var tmplRequestOfficeListItem = '<li>\n' +
    '<a href="/start/"> <i class="fa fa-building-o">&nbsp;</i> O escritório ${office} <br />' +
    'deseja se relacionar com você &nbsp; <i class="fa fa-angle-right"></i>' +
    '</li>\n';

function VerifyInvite() {
    $.ajax({
        type: "GET",
        url: "/convites/verificar/",
        data: {},
        success: function (response) {
            if (response.length) {
                $('#request-list').html('');
                $.each(response, function( index, value ) {
                    if(value.invite_from === 'P') {
                        $.tmpl(tmplRequestPersonListItem, value).appendTo('#request-list');
                    }else{
                        $.tmpl(tmplRequestOfficeListItem, value).appendTo('#request-list');
                    }
                });
                $("#request-notify").removeClass('hide');
            } else {
                $('#request-list').html('<li><strong class="drop-title" id="">Nenhuma solicitação</strong></li>');
                $('#request-notify').addClass('hide');
            }
        },
        dataType: "json"
    });
}

setInterval(function () {
    VerifyInvite();
}, 180000);

$(document).ready(function () {
    VerifyInvite();
});
