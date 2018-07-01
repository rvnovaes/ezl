angular.module('app').controller('chatCtrl', function($scope, $interval, chatApiService,
    $location, $anchorScroll){

  $('.bg-title').css('display', 'none')
  $scope.inMessage = false;
  $scope.hideEmptyChats = true;
  $scope.realContacts = [];
  $scope.contacts = [];
  $scope.chat = {}
  $scope.chatPageSize = 20;
  $scope.chats = [];
  $scope.allChats = [];
  $scope.currentChatPage = 0;
  $scope.chatsLoading = false;
  $scope.sockets = {};
  $scope.messages = []
  $scope.listOffices = true;
  $scope.search = "";
  $scope.chatSelected = {};
  $scope.office_id = false;
  $scope.office_id_since = false;
  $scope.listScrollChat = false
  $scope.existsUnread = false;
  $scope.search = ''

  $('#list-chat-scroll').ready(function(){
    resizeChat();
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
      });
    } else {
      if(oldValue != "" && newValue == ""){
        $scope.chats = $scope.chats = [];
        getChats();
      } else {
        $scope.chats = $scope.allChats.filter(function(contact){
          if (contact.title.toUpperCase().indexOf(newValue.toUpperCase()) !== -1) {
            return contact;
          }
        });
      }
    }
  });

  $scope.$watch('hideEmptyChats', function(newValue, oldValue) {
    getChats();
  });

  $scope.unreadMessage = function(chat){
    data = {
      chat: chat.id
    }
    chatApiService.unreadMessage(data).then(function(data){
      chat.unread_message_quanty = 0;
      $scope.existsUnread = true;
    })
  }

  var readMessage = function(chat){
    data = {
      chat_id: chat.id
    }
    chatApiService.readMessage(data)
    chat.unread_message_quanty = 0;
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
      $scope.office_id_since = new Date();
      $scope.chatsLoading = true;
      $scope.chats = [];
      $scope.allChats = [];
      $scope.currentChatPage = 0;

      chatApiService.getChats($scope.office_id, $scope.hideEmptyChats).then(function(data){
        $scope.chatsLoading = false;
        $scope.allChats = data;
        if (!$scope.search.length) {
            $scope.loadMoreChats();
        }
        setTimeout(function(){
          $scope.listScrollChat.update();
        }, 200);
      })
    }
  };

  /*
  Pega apenas os chats que tiveram atualização desde o carregamento da listagem de chats
  */
  var updateListChats = function(){
      if(! $scope.office_id_since) {
        return false;
      }
      chatApiService.getChats($scope.office_id, $scope.hideEmptyChats, $scope.office_id_since).then(function(data){
        if (data.length > 0) {
          $scope.office_id_since = new Date();
          var moveChatsToTop = function(data, source){
            // Coloca os chats que tiveram atualização no topo da lista
            for (var x=0; x < data.length; x++){
                var new_item = data[x];
                for (var y=0; y < source.length; y++){
                    var source_item = source[y];
                    if (source_item.id == new_item.id){
                        // Remove o item da posição atual na lista
                        source.splice(y, 1);
                    }

                }
                // Adiciona o item no topo da lista
                source.unshift(new_item);
            }
          };
          moveChatsToTop(data, $scope.allChats);

          // Precisamos atualizar a lista que está sendo exibida até a paginação atual
          // Fazemos isso apenas quando a busca não está sendo realizada
          if(!$scope.search.length) {
              var index_to = $scope.currentChatPage * $scope.chatPageSize;
              $scope.chats = $scope.allChats.slice(0, index_to);
          }
        }
      });
  };

  $scope.loadMoreChats = function(chat){
      if (!$scope.office_id && $scope.listOffices) {
        return false;
      }
      if ($scope.search.length) {
        $scope.currentChatPage = 0;
        return false;
      }
      $scope.currentChatPage += 1;
      var index_to = $scope.currentChatPage * $scope.chatPageSize,
          index_from = index_to - $scope.chatPageSize,
          new_page = $scope.allChats.slice(index_from, index_to);
      for(var i=0; i < new_page.length; i++) {
        $scope.chats.push(new_page[i]);
      }
      setTimeout(function(){
          $scope.listScrollChat.update();
      }, 2000);
  };

  $scope.getChats = function(office_id) {
    $scope.office_id = office_id;
    $scope.listOffices = false;
    $scope.search = "";
    getChats()
  }

  update_list_office = $interval(getContacts, 5000)
  update_list_chats = $interval(updateListChats, 5000)

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
