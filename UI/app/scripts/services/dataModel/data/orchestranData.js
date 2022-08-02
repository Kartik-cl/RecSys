'use strict';

angular.module('watsonRetailApp')
  .factory('orchestranData', function (dataAccess, defaultValues, commonUtility) {
    
    var orchestranData = {};
    
    orchestranData.getWatsonResponse = function(postData) {
        return dataAccess.postAsync(commonUtility.getRelativeUrl(defaultValues.ORCHESTRATOR_CHAT_API), postData);
//        return dataAccess.getFromJsonAsync("/scripts/services/constants/request-response.json");
    };
    
    return orchestranData;
  });
