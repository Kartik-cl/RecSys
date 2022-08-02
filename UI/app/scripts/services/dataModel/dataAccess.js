'use strict';

angular.module('watsonRetailApp')
    .service('dataAccess', function (businessUtility, $http) {
    
    function generateHeader() {
        var header = {};
        return header;
    }
    
    this.getAsync = function(relativeUrl){        
        return $http({
            method: 'GET', 
            url: businessUtility.buildUrl(relativeUrl),
            headers: generateHeader()
        });
    };
    
    this.getFromJsonAsync = function(relativeUrl){
        return $http({
            method: 'GET', 
            url: relativeUrl
        });
    };
    
    this.postAsync = function(relativeUrl, postData){
        var httpPromise = null;
        var requestObj = {};
        requestObj = {
            method: 'POST', 
            url: businessUtility.buildUrl(relativeUrl),
            data: postData,
            headers: generateHeader()
        };
        httpPromise = $http(requestObj);
        return httpPromise;
    };
    
    this.putAsync = function(relativeUrl, putData){
        var httpPromise = null;
        var requestObj = {};
        requestObj = {
            method: 'PUT', 
            url: businessUtility.buildUrl(relativeUrl),
            data: putData,
            headers: generateHeader()
        };
        httpPromise = $http(requestObj);
        return httpPromise;
    };
});
