var setBadgeItem = function (items) {
    items.forEach(function (item) {
        var el = $("[badge-id=" + item.message__chat__pk + "]")
        if (item.quantity){
            el.text(item.quantity)
        } else{
            el.text(null)
        }

    })
};

setInterval(function () {
    $.ajax({
        type: "GET",
        url: "/chat/count_message/",
        data: {},
        success: function(response){
            console.log(response.all_messages);
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


