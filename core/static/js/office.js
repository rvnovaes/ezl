var updateInvite = function(invite_pk, status, csrf_token) {
    var data = {}
    data = {
        'invite_pk': invite_pk,
        'status': status
    };
    $.ajax({
        type: 'POST',
        url: '/convites/invite_update/',
        data: data,
        success: function(response){
                window.location.reload();
            },
        beforeSend: function(xhr, settings){
            xhr.setRequestHeader('X-CSRFToken', csrf_token)
        }
    })
}
