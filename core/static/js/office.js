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

// var inviteMultipleUsers = function(elementClass, office, csrf_token){
//     el = $('.' + elementClass);
//     persons = el.val();
//     var data = {
//         persons: persons,
//         office: office
//     };
//     $.ajax({
//         type: 'POST',
//         url: '/convites/convidar',
//         data: data,
//         success: function(response){
//                 console.log(response)
//             },
//         beforeSend: function(xhr, settings){
//             xhr.setRequestHeader('X-CSRFToken', csrf_token)
//         }
//     })
// }
