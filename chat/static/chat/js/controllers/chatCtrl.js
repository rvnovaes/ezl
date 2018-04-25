angular.module('app').controller('chatCtrl', function($scope, $interval, chatApiService,
    $location, $anchorScroll){

  $('.bg-title').css('display', 'none')
  $scope.contacts = [];
  $scope.chats = [];
  $scope.messages = []
  $scope.listOffices = true;
  $scope.search = "";
  $scope.chatSelected = {}
  $scope.socket = {}
  $scope.office_id = false

  var getContacts = function () {
    if ($scope.listOffices) {
      chatApiService.getContacts().then(function(data){
        $scope.contacts = data
      });
    }
  }

  getContacts()

  var getChats = function(){
    if ($scope.office_id && !$scope.listOffices) {
      chatApiService.getChats($scope.office_id).then(function(data){
        $scope.chats = data;
      })
    }
  };

  $scope.getChats = function(office_id) {
    $scope.office_id = office_id
    $scope.listOffices = false;
    getChats()
  }

  update_list_office = $interval(getContacts, 5000)
  update_list_chats = $interval(getChats, 5000)

  $scope.getMessages = function(chat){
    $location.hash('bottom')
    $anchorScroll()
    $scope.chat = chat
    chatApiService.getMessages(chat.id).then(function(data){
      $scope.messages = data
      var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
      $scope.socket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/?label=" + chat.label);
      $scope.socket.onopen = function (data) {
        $scope.socket.send(data);
      };
      $scope.socket.onmessage = function(e){
        if (JSON.parse(e.data).chat === $scope.chat.id){
          $scope.messages.messages.push(JSON.parse(e.data))
          $scope.$apply()
          updateScroll()
        }
      }
    })
  };

  var updateScroll = function(){
    var scrollID = $('#scroll-bottom');
    setTimeout(function(){
      scrollID.scrollTop(scrollID[0].scrollHeight)
    }, 500);
  }

  $scope.sendMessage = function(){
    var data = JSON.stringify({
      'text': $scope.message,
      'chat': $scope.chat.id,
      'label': $scope.chat.label
    });
    $scope.socket.onopen(data);
    updateScroll()
    $scope.message = ""
  }

  $scope.getClass = function(message_user_id, request_user_id){
    if (message_user_id === request_user_id) {
      return 'odd bounceInRight animated'
    }
    return 'bounceInLeft animated'
  }

  $scope.goOfficeList = function(){
    $scope.listOffices = true
  }

  $scope.onEnterKey = function(event){
    if (event.key === 'Enter') {
      $scope.sendMessage()
    }
  }

})
