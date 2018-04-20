angular.module('app').factory('chatApiService', function($http){
  var _getContacts = function(){
    return $http.get('/chat/contact').then(function(response){
      return response.data
    })
  }

  return {
    getContacts: _getContacts
  }
})
