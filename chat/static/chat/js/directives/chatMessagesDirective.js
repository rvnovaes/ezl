angular.module('app').directive("chatMessagesDirective", function(){
  return {
    scope: false, 
    link: function(scope, element, attr){
      var body = $("body");
      $('#chatBox').css({
           'height': (($(window).height()) - 230) + 'px'
       });
      $("#close-message").on('click', function(){
        $(".right-sidebar").slideDown(50).toggleClass("shw-rside");
      })
      var bottomCoord = $('#scroll-bottom')[0].scrollHeight;
      $('#scroll-bottom').slimScroll({scrollTo: bottomCoord});
      $(".fxhdr").on("click", function () {
          body.toggleClass("fix-header"); /* Fix Header JS */
      });
      $(".fxsdr").on("click", function () {
          body.toggleClass("fix-sidebar"); /* Fix Sidebar JS */
      });

      /* ===== Service Panel JS ===== */

      var fxhdr = $('.fxhdr');
      if (body.hasClass("fix-header")) {
          fxhdr.attr('checked', true);
      } else {
          fxhdr.attr('checked', false);
      }
    }
  }
})
