'use strict';

angular.module('watsonRetailApp')
    .config(function($httpProvider, $windowProvider) {
        $httpProvider.defaults.timeout = 60000;
        if(!$httpProvider.defaults.headers.get){
            $httpProvider.defaults.headers.get = {};
        }
        
        var isCacheExecute = true;
        var window = $windowProvider.$get();
        var brs = {chrome: /chrome/i, firefox: /firefox/i, ie: /internet explorer/i};
        for(var k in brs){
            if(brs[k].test(window.navigator.userAgent)){
                isCacheExecute = false;
            }
        }
        if(isCacheExecute){
            $httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
            $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
        }
        
    });