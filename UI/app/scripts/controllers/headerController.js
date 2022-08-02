'use strict';

angular.module('watsonRetailApp')
    .controller('headerController', function ($location, defaultValues, $rootScope){
        
    var vm =  this;
    vm.user = defaultValues.BLANK_STRING;
    vm.showLoader = true;
    $rootScope.$on("loggedUser", function(){
        vm.user = $rootScope.username;
        vm.showLoader = false;
    });
    function initialized() {
        vm.user = defaultValues.BLANK_STRING;
        $rootScope.username = defaultValues.BLANK_STRING;
    };
    
    vm.onLogoutClick = function(){
        vm.user = defaultValues.BLANK_STRING;
        $rootScope.username = defaultValues.BLANK_STRING;
        $location.path("/");
    };
    
    vm.setUser = function(){
        vm.user = $rootScope.username;
    };
    
    initialized();
    
  });
