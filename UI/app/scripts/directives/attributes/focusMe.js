'use strict';

angular.module('watsonRetailApp')
  .directive('focusMe', function ($parse, $timeout) {
    return {
        restrict:"A", // E-Element A-Attribute C-Class M-Comments
        replace: false,
        link: function(scope, element, attrs){
            scope[attrs.focusMe] = element[0];
            element[0].focus();
//            var model = $parse(attrs.focusMe);
//            scope.$watch(model, function(value){
//                if(value){
//                    $timeout(function(){
//                        element[0].focus();
//                    });
//                }
//            });
        }
    };
  });