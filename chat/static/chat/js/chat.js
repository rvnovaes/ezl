setInterval(function () {
    $.ajax({
        type: "GET",
        url: "/chat/count_message/",
        data: {},
        success: function(response){
            $('.chat-badge.badge').text(response.count)
        },
        dataType: "json"
    });
    console.log($('.chat.badge').text())
}, 1000);