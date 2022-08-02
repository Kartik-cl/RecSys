'use strict';

angular.module('watsonRetailApp')
  .service('objectStorage', function () {
    
    var objectStorage = {};
    
    var conversationID = "";
    
    Object.defineProperty(objectStorage, "conversationID", {
        get: function() {
            return conversationID;
        },
        set: function(convID) {
            conversationID = convID;
        }
    });
    
    return objectStorage;
});