'use strict';

angular.module('watsonRetailApp')
    .factory('commonUtility', function (defaultValues) {
    
    var commonUtility = {};
    
    commonUtility.getRelativeUrl = function(relativeUrl){
        return relativeUrl;
    };
    
    commonUtility.is3DValidKey = function(value){
        return (angular.isDefined(value) && 
            value !== defaultValues.BLANK_STRING && value !== null);
    };
    commonUtility.isDefinedObject = function(object){
        return (angular.isObject(object) && angular.isDefined(object) && object !== null);
    };
    
    return commonUtility;
  });
