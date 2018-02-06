var setBadgeItem = function (items) {
    $("[badge-id]").text(null);
    items.forEach(function (item) {
        var el = $("[badge-id=" + item.message__chat__pk + "]");
        if (item.quantity > 0) {
            el.text(item.quantity)
        } else {
            el.text(null)
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

var count_message = setInterval(function () {
    $.ajax({
        type: "GET",
        url: "/chat/count_message/",
        data: {},
        success: function (response) {
            if (response.all_messages > 0) {
                $('.chat-badge.badge').text(response.all_messages)
            } else {
                $('.chat-badge.badge').text(null)
            }
            setBadgeItem(response.grouped_messages)
        },
        dataType: "json"
    });
}, 1000);


var formatDate = function (strDate) {
    return strDate.substr(8, 2) + '/' + strDate.substr(5, 2)+ '/' + strDate.substr(0, 4) + ' ' + strDate.substr(11)
};
