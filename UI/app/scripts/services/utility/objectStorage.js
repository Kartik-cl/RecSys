'use strict';

angular.module('watsonRetailApp')
  .service('objectStorage', function () {
    
    var objectStorage = {};
    
    var baseUrl = "";   
    
    
    Object.defineProperty(objectStorage, "baseUrl", {
        get: function() {
            return baseUrl;
        },
        set: function(url) {
            baseUrl = url;
        }
    });
    
    return objectStorage;
});