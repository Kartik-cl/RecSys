'use strict';

angular.module('watsonRetailApp')
    .factory('businessUtility', function (objectStorage) {
    
    var businessUtility = {}; 
    var baseUrl = "http://127.0.0.1:8080/api/v1"   
   
    businessUtility.buildUrl = function(relativeUrl){
        return baseUrl + relativeUrl;
    };
        
    return businessUtility;
  });