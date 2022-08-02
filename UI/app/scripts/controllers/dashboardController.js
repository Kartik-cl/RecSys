'use strict';

angular.module('watsonRetailApp')
    .controller('dashboardController', function ($rootScope, orchestranBusiness, 
        objectStorage, defaultValues, applicationProperties, commonUtility, $timeout, $interval){
        
    var vm =  this;
    vm.loggedUser = {};
    vm.userInput = defaultValues.BLANK_STRING;
    vm.watsonChat = [];
    vm.contextId = defaultValues.BLANK_STRING;
    var numOfCall = 0;
    vm.recommendType = defaultValues.BLANK_STRING;
    vm.endOfChat = false;
    var miniListItemCountShow = 4;
    vm.txtSearchBox = defaultValues.BLANK_STRING;
    vm.isListShow = false;
    vm.listLimitToShow = miniListItemCountShow;
    vm.list = [];
    vm.selectedItem = defaultValues.BLANK_STRING;
    vm.recommendations = [];
    vm.imageBase64 = "data:image/png;base64,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";
    vm.userTypingText = "Typing ...";
    vm.watsonTypingText = "Loading ...";
    vm.isTypingOrThinking = false;
    
    var intervalTyping = $interval(onTypingOrThinking, 1400);
	
    function initialized(){
        vm.endOfChat = false;
        vm.user = $rootScope.username;
        vm.response = [];
        var postData = {};
        postData.userID = vm.user;
        postData.inputMessage = defaultValues.BLANK_STRING;
        setChatData(true);
            
        orchestranBusiness.getWatsonResponse(postData).then(function(response) {
            var data = response.data;
            if(commonUtility.isDefinedObject(data.userDetail)){
                vm.loggedUser = data.userDetail;
                $rootScope.username = vm.loggedUser.first_name;                
                $rootScope.$broadcast("loggedUser");
            }
            numOfCall = 1;
            if(commonUtility.isDefinedObject(data.outputMessages) && data.outputMessages.length > 0 ){
                var message = defaultValues.BLANK_STRING;
                for(var index=0; index<data.outputMessages.length; index++){
                    message = message + data.outputMessages[index] + "\n";
                }
                setChatProperty("watson", message);
                setChatProperty("watsonTyping", false);
                setChatProperty("showList   ", false);
                setChatData(false);
            }
            objectStorage.conversationID = data.conversationID;
        });
    }
    
    function onTypingOrThinking(){
        vm.isTypingOrThinking = !vm.isTypingOrThinking;
    }
    
    function getNextAttributePrediction(nextAttribute) {
        if(commonUtility.isDefinedObject(nextAttribute)) {
            if(commonUtility.is3DValidKey(nextAttribute["values"])) {
                vm.list = nextAttribute["values"];
            }
            if(commonUtility.is3DValidKey(nextAttribute["question"])) {
                return nextAttribute["question"];
            }
        }
        return defaultValues.BLANK_STRING;
    }
    
    function setChatData(isWatsonThinking){
        var chat = {
            userTyping: false,
            watsonTyping: isWatsonThinking,
            recommendations:false,
            user: defaultValues.BLANK_STRING,
            watson: defaultValues.BLANK_STRING,
            selectedItem: defaultValues.BLANK_STRING
        };
        vm.watsonChat.push(chat);
    }
    
    function setChatProperty(propertyName, value, index){
        if(vm.watsonChat.length > 0){
            var idx = vm.watsonChat.length - 1;
            if(commonUtility.is3DValidKey(index)){
                idx = index;
            }
            vm.watsonChat[idx][propertyName] = value;
        }
    }
    
    vm.onOptForPurchaseClick = function(option, product){
        if(angular.isDefined(objectStorage.conversationID) && objectStorage.conversationID !== null){
            var postData = {};
            
            postData.userID = vm.user;
            postData.product = {};
            postData.inputMessage = defaultValues.BLANK_STRING;
            postData.conversationID = objectStorage.conversationID;
            postData.data = {};
            var requestData = {
                purchase: option
            };
            postData.data = requestData;
            setChatProperty("watsonTyping", false, (numOfCall-1));
            setChatProperty("userTyping", false, (numOfCall-1));
            setChatProperty("recommendations", false, (numOfCall-1));
            setChatProperty("styleRecommend", false, (numOfCall-1));
            setChatProperty("isViewRelatedProducts", false, (numOfCall-1));
            setChatData(true);
            orchestranBusiness.getWatsonResponse(postData).then(function(response) {
                var data = response.data;
                numOfCall = numOfCall + 1;
                if(commonUtility.isDefinedObject(data.outputMessages) && data.outputMessages.length > 0 ){
                    var message = defaultValues.BLANK_STRING;
                    for(var index=0; index<data.outputMessages.length; index++){
                        message = message + data.outputMessages[index] + "\n";
                    }
                    setChatProperty("watson", message);
                    setChatProperty("user", defaultValues.BLANK_STRING);
                    setChatProperty("showList", false);
                    setChatProperty("isViewRelatedProducts", false);
                    setChatProperty("watsonTyping", false);
                    setChatProperty("userTyping", false);
                    if(commonUtility.isDefinedObject(requestData) && commonUtility.is3DValidKey(requestData.purchase) 
                            && requestData.purchase === "yes" && commonUtility.isDefinedObject(product)){
                        setChatProperty("isViewRelatedProducts", true);
                        setChatProperty("selectedProduct", angular.copy(product));
                    }
                }
                setChatData(false);
            });
            
        }
    };
    
    vm.onUserInputClick = function(chatIndex, isSelect) {
        vm.watsonTypingText = "Loading...";
        if(commonUtility.is3DValidKey(isSelect) && isSelect && commonUtility.is3DValidKey(chatIndex) && chatIndex >= 0){
            if(commonUtility.is3DValidKey(vm.watsonChat[chatIndex].selectedItem)){
                vm.watsonChat[chatIndex].user = angular.copy(vm.watsonChat[chatIndex].selectedItem);
            }else if(commonUtility.is3DValidKey(vm.watsonChat[chatIndex].viewRelatedProduct)){
                vm.watsonChat[chatIndex].user = angular.copy(vm.watsonChat[chatIndex].viewRelatedProduct);                
                setChatProperty("viewRelatedProduct", vm.watsonChat[chatIndex].viewRelatedProduct);
            }            
        }else{
            if(vm.userInput === defaultValues.BLANK_STRING){
                return;
            }
            setChatProperty("user", angular.copy(vm.userInput));
            setChatProperty("userTyping", false);
        }
        vm.userInput = defaultValues.BLANK_STRING;
        if(angular.isDefined(objectStorage.conversationID) && objectStorage.conversationID !== null){
            var postData = {};
            postData.userID = vm.user;
            postData.inputMessage = (commonUtility.is3DValidKey(isSelect) && isSelect 
                    && commonUtility.is3DValidKey(chatIndex) && chatIndex >= 0) ?
                    vm.watsonChat[chatIndex].user : vm.watsonChat[vm.watsonChat.length - 1].user;
            postData.conversationID = objectStorage.conversationID;
            if(commonUtility.is3DValidKey(isSelect) && isSelect && commonUtility.is3DValidKey(chatIndex) && chatIndex >= 0){
                if(commonUtility.is3DValidKey(vm.watsonChat[chatIndex].viewRelatedProduct)) {
                    postData.data = {};
                    var requestData = {
                        viewRelatedProduct: vm.watsonChat[chatIndex].viewRelatedProduct
                    };
                    postData.data = requestData;
                    if(commonUtility.isDefinedObject(requestData) && commonUtility.is3DValidKey(requestData.viewRelatedProduct)
                            && requestData.viewRelatedProduct === "yes" && commonUtility.isDefinedObject(vm.watsonChat[chatIndex])
                            && commonUtility.isDefinedObject(vm.watsonChat[chatIndex].selectedProduct)){
                        var product = vm.watsonChat[chatIndex].selectedProduct;
                        postData.product = {};
                        postData.product.conversation_id = objectStorage.conversationID;
                        postData.product.selected_product_id = product.product_index;
                        postData.product.selected_product_image_URI = product.image_src.split(",")[1];
                    }
                }
            }
            setChatProperty("watsonTyping", false, (numOfCall-1));
            setChatProperty("userTyping", false, (numOfCall-1));
            setChatProperty("recommendations", false, (numOfCall-1));
            setChatData(true);
            
            callOrchestrator(postData, chatIndex)
        }
    };
    
    function callOrchestrator(postData, chatIndex) {
        orchestranBusiness.getWatsonResponse(postData).then(function(response) {
            var data = response.data;
            numOfCall = numOfCall + 1;;

            if(commonUtility.isDefinedObject(data.outputMessages) && data.outputMessages.length > 0 ){
                var message = defaultValues.BLANK_STRING;
                for(var index=0; index<data.outputMessages.length; index++){
                    message = message + data.outputMessages[index] + "\n";
                }
                setChatProperty("watson", message);
                setChatProperty("user", defaultValues.BLANK_STRING);
                setChatProperty("showList", false);
                setChatProperty("isViewRelatedProducts", false);
                setChatProperty("watsonTyping", false);
                setChatProperty("userTyping", false);
            } else if(commonUtility.isDefinedObject(data.nextAttribute)) {
                setChatProperty("watson", getNextAttributePrediction(data.nextAttribute));
                setChatProperty("user", defaultValues.BLANK_STRING);
                setChatProperty("selectedItem", defaultValues.BLANK_STRING);
                setChatProperty("naValues", vm.list);
                setChatProperty("showList", true);
                setChatProperty("listLimitToShow", ((vm.list.length > miniListItemCountShow) ? miniListItemCountShow : vm.list.length));
                setChatProperty("isMore", (vm.list.length > miniListItemCountShow));
                setChatProperty("watsonTyping", false);
                setChatProperty("userTyping", false);
            }
            if(commonUtility.isDefinedObject(data.products) && data.products.length > 0){

                if(vm.watsonChat[chatIndex].viewRelatedProduct === "yes"){
                    vm.watsonChat[vm.watsonChat.length - 1].recommendations = false;
                    vm.watsonChat[vm.watsonChat.length - 1].styleRecommend = true;
                    vm.watsonChat[vm.watsonChat.length - 1].isViewRelatedProducts = false;
                } else {
                    vm.watsonChat[vm.watsonChat.length - 1].recommendations = true;
                    vm.watsonChat[vm.watsonChat.length - 1].styleRecommend = false;
                }
                vm.watsonChat[vm.watsonChat.length - 1].products = [];
                vm.watsonChat[vm.watsonChat.length - 1].products = angular.copy(data.products);
            }
            setChatData(false);
        });        
    }

    vm.onChangeInput = function() {
        setChatProperty("userTyping", (vm.userInput !== defaultValues.BLANK_STRING));
    };
    
    vm.onItemSelect = function(chatIndex,item){
        if(commonUtility.is3DValidKey(chatIndex)
                && commonUtility.is3DValidKey(item)){
            vm.watsonChat[chatIndex].selectedItem = item;
        }
        $timeout(function(){
            vm.onUserInputClick(chatIndex, true);
        }, 400);
    };
    
    vm.onMoreDataClick = function(chatIndex){
        vm.watsonChat[chatIndex].isMore = !vm.watsonChat[chatIndex].isMore;
        vm.watsonChat[chatIndex].listLimitToShow = vm.watsonChat[chatIndex].showList ? vm.watsonChat[chatIndex].naValues.length : miniListItemCountShow;
    };
    
    vm.isRelatedCick = function(chatIndex, isRelatedProductQuery){
        if(commonUtility.is3DValidKey(chatIndex) && chatIndex >=0){
            vm.watsonChat[chatIndex].viewRelatedProduct = isRelatedProductQuery;
        }
        $timeout(function(){
            vm.onUserInputClick(chatIndex, true);
        }, 400);
    };
    
    vm.onShowMoreClick = function(product) {
        if(angular.isDefined(objectStorage.conversationID) && objectStorage.conversationID !== null){
            var postData = {};
            
            postData.userID = vm.user;
            postData.product = {};
            postData.inputMessage = defaultValues.BLANK_STRING;
            postData.conversationID = objectStorage.conversationID;
            postData.data = {};
            var requestData = {
                showMoreProduct: "yes",
                similarProducts: product.similar_products
            };
            postData.data = requestData;
            setChatProperty("watsonTyping", false, (numOfCall-1));
            setChatProperty("userTyping", false, (numOfCall-1));
            setChatProperty("recommendations", false, (numOfCall-1));
            setChatProperty("styleRecommend", false, (numOfCall-1));
            setChatProperty("isViewRelatedProducts", false, (numOfCall-1));
            setChatProperty("isShowMoreProducts", false, (numOfCall-1));
            setChatProperty("showList", false);
            vm.watsonTypingText = "Watson Recommendence is searching...";
            setChatData(true);
            orchestranBusiness.getWatsonResponse(postData).then(function(response) {
                var data = response.data;
                numOfCall = numOfCall + 1;
                if(commonUtility.isDefinedObject(data.outputMessages) && data.outputMessages.length > 0 ){
                    var message = defaultValues.BLANK_STRING;
                    for(var index=0; index<data.outputMessages.length; index++){
                        message = message + data.outputMessages[index] + "\n";
                    }
                    setChatProperty("watson", message);
                    setChatProperty("user", defaultValues.BLANK_STRING);
                    setChatProperty("showList", false);
                    setChatProperty("isShowMoreProducts", true);
                    setChatProperty("watsonTyping", false);
                    setChatProperty("userTyping", false);            
                }
                if(commonUtility.isDefinedObject(data.products) && data.products.length > 0){
//                    vm.endOfChat = true;
                    vm.watsonChat[vm.watsonChat.length - 1].recommendations = false;
                    vm.watsonChat[vm.watsonChat.length - 1].styleRecommend = true;
                    vm.watsonChat[vm.watsonChat.length - 1].products = [];
                    vm.watsonChat[vm.watsonChat.length - 1].products = angular.copy(data.products);
                }
                setChatData(false);
            });
        }
    };
    
    initialized();
    
  });
