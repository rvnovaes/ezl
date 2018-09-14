angular.module('app', ['ui.event', 'infinite-scroll'])
  .config(['$httpProvider', function ($httpProvider) {
    /* csrf */
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  }])
