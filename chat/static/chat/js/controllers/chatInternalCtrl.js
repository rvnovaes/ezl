angular.module('app').controller('chatInternalCtrl', function($scope, chatApiService){
  $scope.chat_id = false;
  $scope.in_office_list = true;
  $scope.offices = [];
  $scope.messages = [];
  $scope.getChatContacts = function(task_id, chat_id){
    $scope.task_id = task_id
    $scope.chat_id = chat_id
    chatApiService.getInternalChatOffices(task_id).then(function(data){
      $scope.offices = data
    })
  }

  $scope.getMessages = function(chat){
    chatApiService.getMessages(chat).then(function(data){
      $scope.messages = data;
      console.debug($scope.messages)
    })
    $scope.in_office_list = false;
  }



})
