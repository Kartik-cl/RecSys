'use strict';

angular.module('watsonRetailApp')
    .controller('loginController', function ($location, $rootScope, objectStorage){
        
    var vm =  this;
    vm.username = "";
    $rootScope.isLogin = false;
    $rootScope.username = "User";
    vm.isImg = false;
    
    vm.imgOnClick = function(){
        vm.isImg = true;
    };
    function initialize(){
        $rootScope.isLogin = false;
        $rootScope.username = "";
        objectStorage.conversationID = null;
    }
    
    vm.onLoginClick = function(){
        $location.path("recommendence");
        $rootScope.isLogin = true;
        $rootScope.username = vm.username;
        objectStorage.conversationID = null;
        
    };
    
    vm.onGuestClick = function(){
        $location.path("recommendence");
        $rootScope.isLogin = true;
        $rootScope.username = "Guest";
    };
    
    initialize();
    
  });
