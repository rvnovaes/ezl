angular.module('app').factory('chatApiService', function($http){
  var _getContacts = function(){
    return $http.get('/chat/contact').then(function(response){
      return response.data
    })

  }

  var _getChats = function(office_id, exclude_empty, since){
    if (since === undefined){
      since = "";
    } else {
      since = since.getFullYear() + "-" + (since.getMonth()+1) + "-" + since.getDate() + "T" + since.getHours() + ":" + since.getMinutes() + ":" + since.getSeconds();
    }
    return $http.get('/chat/chats_by_office/', {params: {office:office_id, since: since, exclude_empty: exclude_empty}}).then(function(response){
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

  var _getInternalChatOffices = function(task_id){
    return $http.get('/chat/internal_chat_offices/', {params: {task: task_id}}).then(function(response){
      return response.data
    })
  }

  var _unreadMessage = function(data) {
    return $http.post('/chat/unread_message/', data).then(function(response){
      return response.data
    })
  }

  return {
    getContacts: _getContacts,
    getChats: _getChats,
    getMessages: _getMessages,
    newSocket: _newSocket,
    readMessage: _readMessage,
    getInternalChatOffices: _getInternalChatOffices,
    unreadMessage: _unreadMessage
  }
})
