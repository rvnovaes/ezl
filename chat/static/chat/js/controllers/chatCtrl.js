angular.module('app').controller('chatCtrl', function($scope, $interval, chatApiService){
  $scope.contacts = [];
  $scope.chats = [];
  $scope.messages = []
  $scope.listOffices = true;
  $scope.search = "";
  $scope.chatSelected = {}
  $scope.socket = {}
    // update_list = $interval(function(){
    //   chatApiService.getContacts().then(function(data){
    //     $scope.contacts = data
    //   })
    // }, 1000)

  chatApiService.getContacts().then(function(data){
    $scope.contacts = data
    $scope.listOffices = true;
  });

  $scope.getChats = function(office_id){
    chatApiService.getChats(office_id).then(function(data){
      $scope.listOffices = false;
      $scope.chats = data;
    })
  };

  $scope.getMessages = function(chat){
    $scope.chat = chat
    chatApiService.getMessages(chat.id).then(function(data){
      $scope.messages = data
      $scope.socket = chatApiService.newSocket(chat.label)
      $scope.socket.onopen = function (data) {
        $scope.socket.send(data);
      };
      $scope.socket.onmessage = function(e){
        console.debug(e)
        $scope.messages.messages.push(JSON.parse(e.data))
      }
    })
  };

  $scope.sendMessage = function(){
    var data = JSON.stringify({
      'text': $scope.message,
      'chat': $scope.chat.id,
      'label': $scope.chat.label
    })
    $scope.socket.onopen(data)
  }

  $scope.getClass = function(message_user_id, request_user_id){
    if (message_user_id === request_user_id) {
      return 'odd bounceInRight animated'
    }
    return 'bounceInLeft animated'
  }


})
