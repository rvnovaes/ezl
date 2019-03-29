/*jslint browser: true*/
/*global $, jQuery, alert*/

$(document).ready(function () {

    "use strict";

    $('.slimScroll').slimScroll({
        height: ($(window).height()) - 160 + 'px',
        color: '#aaaaaa'
    });
    $(function () {
        $(window).on("load", function () { // On load
            $('.slimscroll').css({
                'height': (($(window).height()) - 160) + 'px'
            });
        });
        $(window).on("resize", function () { // On resize
            $('.slimScroll').css({
                'height': (($(window).height()) - 160) + 'px'
            });
        });
    });

    // this is for the left-aside-fix in content area with scroll

    $(function () {
        $(window).on("load", function () { // On load
            $('.chat-left-inner').css({
                'height': (($(window).height()) - 140) + 'px'
            });
        });
        $(window).on("resize", function () { // On resize
            $('.chat-left-inner').css({
                'height': (($(window).height()) - 140) + 'px'
            });
        });
    });


    $(".open-panel").on("click", function () {
        $(".chat-left-aside").toggleClass("open-pnl");
        $(".open-panel i").toggleClass("ti-angle-left");
    });

});
