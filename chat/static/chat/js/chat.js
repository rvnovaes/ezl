var setBadgeItem = function (items) {
    items.forEach(function (item) {
        var elm = $('#notify-' + item.message__chat__pk)
        if (item.quantity > 0) {
            elm.removeClass('hide');
            elm.text(item.quantity)
        } else {
            elm.addClass('hide')
        }

    })
};


var chatReadMessage = function (chat_id, csrf_token) {
    $.ajax({
        type: 'POST',
        url: '/chat/chat_read_messages',
        data: {
            chat_id: chat_id
        },
        success: function (response) {

        },
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        },
        dataType: 'json'
    })
};

setInterval(function () {
    $.ajax({
        type: "GET",
        url: "/chat/count_message/?has_groups=" + false,
        data: {},
        success: function (response) {
            if (response.all_messages > 0) {
                $("#chat-notify").removeClass('hide');
                $("#li-message-center").removeClass('hide');
                $("#message-center").removeClass('hide');

                if (response.all_messages == 1) {
                    $("#drop-title").html(response.all_messages + ' mensagem não lida');
                } else {
                    $("#drop-title").html(response.all_messages + ' mensagens não lidas');
                }
            } else {
                $("#drop-title").html('0 mensagem não lida');
                $("#chat-notify").addClass('hide');
                $("#li-message-center").addClass('hide');
                $("#message-center").addClass('hide');
            }
        },
        dataType: "json"
    });
}, 5000);


var formatDate = function (strDate) {
    return strDate.substr(8, 2) + '/' + strDate.substr(5, 2)+ '/' + strDate.substr(0, 4) + ' ' + strDate.substr(11)
};
