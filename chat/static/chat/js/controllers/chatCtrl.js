angular.module('app').controller('chatCtrl', function($scope, $interval, chatApiService){
  $scope.contacts = [];
  $scope.pesquisa = "";

  update_list = $interval(function(){
    chatApiService.getContacts().then(function(data){
      $scope.contacts = data
    })

  }, 3000)
})
