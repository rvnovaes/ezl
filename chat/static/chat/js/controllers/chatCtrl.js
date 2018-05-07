angular.module('app').controller('chatCtrl', function($scope, $interval, chatApiService,
    $location, $anchorScroll){

  $('.bg-title').css('display', 'none')
  $scope.inMessage = false;
  $scope.realContacts = [];
  $scope.contacts = [];
  $scope.chat = {}
  $scope.chats = [];
  $scope.realChats = [];
  $scope.sockets = {};
  $scope.messages = []
  $scope.listOffices = true;
  $scope.search = "";
  $scope.chatSelected = {}
  $scope.office_id = false
  $scope.listScrollChat = false
  $scope.existsUnread = false;
  $scope.search = ''

  $('#list-chat-scroll').ready(function(){
    $scope.listScrollChat = new PerfectScrollbar('#list-chat-scroll', {
      wheelSpeed: 2
    })
  });

  $scope.$watch('search', function(newValue, oldValue) {
    if ($scope.listOffices) {
      $scope.contacts = $scope.realContacts.filter(function(contact){
        if (contact.legal_name.toUpperCase().indexOf(newValue.toUpperCase()) !== -1) {
          return contact;
        }
      })
    } else {
      $scope.chats = $scope.realChats.filter(function(contact){
        if (contact.title.toUpperCase().indexOf(newValue.toUpperCase()) !== -1) {
          return contact;
        }
      })
    }
  });

  $scope.unreadMessage = function(chat){
    data = {
      chat: chat.id
    }
    chatApiService.unreadMessage(data).then(function(data){
      setTimeout(getChats, 500);
      $scope.existsUnread = true;
    })
  }

  var readMessage = function(chat){
    data = {
      chat_id: chat.id
    }
    chatApiService.readMessage(data)
    setTimeout(getChats, 500)
    $scope.existsUnread = false;
  }

  var getContacts = function () {
    if ($scope.listOffices) {
      chatApiService.getContacts().then(function(data){
        $scope.realContacts = data;
        if (!$scope.search.length) {
          $scope.contacts = data;
        }
      });
    }
  }

  getContacts()

  var getChats = function(){
    if ($scope.office_id && !$scope.listOffices) {
      chatApiService.getChats($scope.office_id).then(function(data){
        $scope.realChats = data;
        if (!$scope.search.length) {
            $scope.chats = data;
        }
        setTimeout(function(){
          $scope.listScrollChat.update();
        }, 200)
      })
    }
  };

  $scope.getChats = function(office_id) {
    $scope.office_id = office_id
    $scope.listOffices = false;
    $scope.search = "";
    getChats()
  }

  update_list_office = $interval(getContacts, 5000)
  update_list_chats = $interval(getChats, 5000)

  $scope.getMessages = function(chat){
    $scope.inMessage = true;
    $location.hash('bottom')
    $anchorScroll()
    $scope.chat = chat
    chatApiService.getMessages(chat.id).then(function(data){
      $scope.messages = data
      var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
      if (!$scope.sockets[chat.id] ||
        ($scope.sockets[chat.id] && $scope.sockets[chat.id].readyState !=WebSocket.OPEN)){
          $scope.sockets[chat.id] = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/?label=" + chat.label);
          $scope.sockets[chat.id].onopen = function (data) {
              $scope.sockets[chat.id].send(data);
          };
          $scope.sockets[chat.id].onmessage = function(e){
            if (JSON.parse(e.data).chat === $scope.chat.id){
              $scope.messages.messages.push(JSON.parse(e.data))
              $scope.$apply()
              updateScroll()
            }
          }
      }
      readMessage(chat)
    })
  };

  var updateScroll = function(){
    var scrollID = $('#scroll-bottom');
    setTimeout(function(){
      scrollID.scrollTop(scrollID[0].scrollHeight)
    }, 500);
  }

  $scope.sendMessage = function(){
    if ($scope.message) {
      var data = JSON.stringify({
        'text': $scope.message,
        'chat': $scope.chat.id,
        'label': $scope.chat.label
      });
      $scope.sockets[$scope.chat.id].onopen(data);
      updateScroll()
      $scope.message = ""
    }
  }

  $scope.getClass = function(message_user_id, request_user_id){
    if (message_user_id === request_user_id) {
      return 'odd bounceInRight animated'
    }
    return 'bounceInLeft animated'
  }

  $scope.goToOfficeList = function(){
    $scope.listOffices = true
    $scope.search = '';
    $scope.inMessage = false;
    getContacts()
  };

  $scope.onEnterKey = function(event){
    if (event.key === 'Enter') {
      $scope.sendMessage()
    }
  };
})
