'use strict';

angular.module('watsonRetailApp')
  .factory('orchestranBusiness', function (orchestranData) {
    
    var orchestranBusiness = {};
    
      orchestranBusiness.getWatsonResponse = function(postData) {
          return orchestranData.getWatsonResponse(postData);
      };
    
    return orchestranBusiness;
  });
