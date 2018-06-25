var updateInvite = function(invite_pk, status, csrf_token, url_invite) {
    var url = '/convites/invite_update/';
    if (url_invite){
        url = url_invite;
    }
    var data = {};
    data = {
        'invite_pk': invite_pk,
        'status': status,
    };
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: function(response){
                window.location.reload();
            },
        beforeSend: function(xhr, settings){
            xhr.setRequestHeader('X-CSRFToken', csrf_token);
        }
    });
};
