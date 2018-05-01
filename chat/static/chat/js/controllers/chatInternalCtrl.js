angular.module('app').controller('chatInternalCtrl', function($scope, chatApiService){
  vm = this;
  vm.chat_id = false;
  vm.in_office_list = true;
  vm.offices = [];
  vm.messages = [];
  vm.messageToSend = "";
  vm.chat = {};
  vm.getChatContacts = function(task_id, chat_id){
    vm.task_id = task_id;
    vm.chat_id = chat_id;
    vm.chat['id'] = chat_id;
    vm.chat['label'] = "task-" + chat_id;
    chatApiService.getInternalChatOffices(task_id).then(function(data){
      vm.offices = data
    })
  }

  var updateScroll = function(){
    var scrollID = $('#scroll-bottom');
    setTimeout(function(){
      scrollID.scrollTop(scrollID[0].scrollHeight)
    }, 500);
  }


  vm.getMessages = function(chat){
    chatApiService.getMessages(chat).then(function(data){
      vm.messages = data;
      vm.in_office_list = false;
      var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
      vm.socket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/?label=" + vm.chat.label);
      vm.socket.onopen = function (data) {
        vm.socket.send(data);
      };
      vm.socket.onmessage = function(e){
        if (JSON.parse(e.data).chat === vm.chat.id){
          vm.messages.messages.push(JSON.parse(e.data))
          $scope.$apply()
          updateScroll()
        }
      }
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
    var data = JSON.stringify({
      'text': vm.messageToSend,
      'chat': vm.chat.id,
      'label': vm.chat.label
    });
    vm.socket.onopen(data);
    updateScroll()
    vm.messageToSend = ""
  }

  vm.onEnterKey = function(event){
    if (event.key === 'Enter') {
      vm.sendMessage()
    }
  };

})
