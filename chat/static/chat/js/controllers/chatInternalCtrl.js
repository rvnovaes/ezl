angular.module('app').controller('chatInternalCtrl', function($scope, chatApiService){
  vm = this;
  vm.chat_id = false;
  vm.in_office_list = true;
  vm.offices = [];
  vm.messages = [];
  vm.messageToSend = "";
  vm.sockets = {};
  vm.chat = {};
  vm.slideDownSidebar = function(){
    debugger;
    $(".right-sidebar").slideDown(50).toggleClass("shw-rside");
  }
  vm.updateScroll = function(){
    setTimeout(function(){
      var scrollID = $('ul#scroll-bottom.chat-list');
      scrollID.scrollTop(scrollID[0].scrollHeight);
    }, 500)
  }
  vm.getChatContacts = function(task_id, chat_id){
  vm.slideDownSidebar();
  vm.task_id = task_id;
  vm.chat_id = chat_id;
  chatApiService.getInternalChatOffices(task_id).then(function(data){
    vm.offices = data
    })
  }

  vm.getMessages = function(chat){
    chatApiService.getMessages(chat).then(function(data){
      vm.messages = data;
      vm.in_office_list = false;
      vm.chat = data.chat
      console.debug(vm.chat)
      var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
      if (!vm.sockets[vm.chat.id] ||
        (vm.sockets[vm.chat.id] && vm.sockets[vm.chat.id].readyState != WebSocket.OPEN)){
          vm.sockets[vm.chat.id] = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/?label=" + vm.chat.label);
          vm.sockets[vm.chat.id].onopen = function (data) {
              vm.sockets[vm.chat.id].send(data);
          };
          vm.sockets[vm.chat.id].onmessage = function(e){
            if (JSON.parse(e.data).chat === vm.chat.id){
              vm.messages.messages.push(JSON.parse(e.data))
              $scope.$apply()
              vm.updateScroll()
            }
          }
      }
      vm.updateScroll()
    })
  }

  vm.getClass = function(message){
    if (message.create_user_id === vm.messages.request_user_id) {
      return "odd"
    }
    return ""
  }

  vm.setListState = function(){
    vm.in_office_list =! vm.in_office_list;
  }

  vm.sendMessage = function(){
    if (vm.messageToSend) {
      var data = JSON.stringify({
        'text': vm.messageToSend,
        'chat': vm.chat.id,
        'label': vm.chat.label
      });
      vm.sockets[vm.chat.id].onopen(data);
      vm.updateScroll()
      vm.messageToSend = ""

    }
  }

  vm.onEnterKey = function(event){
    if (event.key === 'Enter') {
      vm.sendMessage()
    }
  };

})
