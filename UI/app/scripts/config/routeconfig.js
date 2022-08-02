'use strict';

angular.module('routerConfigModule', ['ngRoute'])
  .config(['$routeProvider','$locationProvider', function($routeProvider, $locationProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'view/login.html'
        })
        .when('/recommendence', {
            templateUrl: 'view/dashboard.html'
        })
        .otherwise({
            redirectTo: '/'
        })
        $locationProvider.html5Mode(true);
  }
]);
