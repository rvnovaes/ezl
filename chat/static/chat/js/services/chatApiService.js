angular.module('app').factory('chatApiService', function($http){
  var _getContacts = function(){
    return $http.get('/chat/contact').then(function(response){
      return response.data
    })

  }

  var _getChats = function(office_id){
    return $http.get('/chat/chats_by_office/', {params: {office:office_id}}).then(function(response){
      return response.data
    })
  }

  var _getMessages = function(chat_id){
    return $http.get('/chat/chat_messages/', {params: {chat: chat_id}}).then(function(response){
      return response.data
    })
  }

  var _newSocket = function(label){
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    return new WebSocket(ws_scheme + "://" + window.location.host + "/ws/?label=" + label);
  }

  var _readMessage = function(data) {
    return $http.post('/chat/chat_read_messages?format=json', data).then(function(response){
      return response.data
    })
  }

  return {
    getContacts: _getContacts,
    getChats: _getChats,
    getMessages: _getMessages,
    newSocket: _newSocket,
    readMessage: _readMessage
  }
})
