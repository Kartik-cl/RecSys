'use strict';

angular.module('watsonRetailApp')
    .filter('startWithFilter', function () {
        return function(list, value) {
            var lowerStr = (value + "").toLowerCase();
            var result = [];
            if(list === null || angular.isUndefined(list) || list.length === 0){
                return result;
            }
            for(var index=0; index<list.length; index++){
                if(list[index].toLowerCase().indexOf(lowerStr) === 0){
                    result.push(list[index]);
                }
            }
            return result;
        };
    });