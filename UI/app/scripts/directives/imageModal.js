'use strict';

angular.module('watsonRetailApp')
  .directive('imageModal', function () {
    return {
	restricted: "E",
	replace: true,
        require: '^form',
        scope: {
            imgSrc: "@",
            imgLabel: "@",
            isShowMore: "@",
            optPurchase: "&",
            isOptPurchase: "=",
            showMore: "&"
//            imgOnClick: "&"
        },
        template: function(){
            var html =  '<div class="thmb-pic1">'+
                            '<div class="thmb-lbl" ng-class="{\'thmb-lbl-incrsd-h\': isShowMore!==\'Y\'}" ' +
                                'ng-mouseenter="onMouseEnterInProduct()"  ng-mouseleave="onMouseLeaveFromProduct()">' +
                                '<div class="img-cont-div">' +  
                                    '<div class="img-buy-div" ng-if="isProductSaleOptionShow">Want to buy?</div>' +
                                    '<div class="img-buy-x-div" ng-if="isProductSaleOptionShow" ng-click="onOptPurchase(\'no\')")>No</div>' +
                                    '<div class="img-buy-y-div" ng-if="isProductSaleOptionShow" ng-click="onOptPurchase(\'yes\')">Yes</div>' +
                                    '<img id="myImg" src="{{imgSrc}}" ng-click="imgOnClick()" alt="{{imgLabel}}" class="imgsize" ng-class="{\'imgsize1\': isProductSaleOptionShow}">' +
                                '</div>' +
                                '<div class="productlabel">'+
                                    '<span >{{imgLabel}}</span>'+
                                '</div>'+
                            '</div>'+
                            '<div class="show-more-label" ng-click="showMore()" ng-if="isShowMore===\'Y\'">'+
                                '<span>Show more</span>'+
                            '</div>'+
                            '<div id="myModal" class="modal">'+
                                '<span class="close" ng-click="onCloseClick()">&times;</span>' +
                                '<img class="modal-content" id="img01">' +
                                '<div id="caption"></div>' +
                            '</div>'+
                        '</div>' ;
        
            return html;
        },
        link: function(scope, element, attrs, formCtrl){
            var src = attrs.hasOwnProperty("src");
           var modal = element.find('#myModal');
           var img = element.find('#myImg');
           var modalImg = element.find("#img01");
           var captionText = element.find("#caption");
            scope.isProductSaleOptionShow = false;
            
            scope.onOptPurchase = function(userInput){
                console.log(userInput);
                scope.optPurchase({
                    option: userInput
                });
            };
            
            scope.onMouseEnterInProduct = function(){
               if(scope.isOptPurchase){
                    scope.isProductSaleOptionShow = true;
                }
           };

           scope.onMouseLeaveFromProduct = function(){
               if(scope.isOptPurchase)
                    scope.isProductSaleOptionShow = false;
           };
		   
           scope.imgOnClick = function(){
               modal[0].style.display = "block";
               modalImg[0].src = scope.imgSrc;
//                captionText.innerHTML = this.alt;
           };
           
           scope.onCloseClick = function() {
               modal[0].style.display = "none";
           };
//           img.onclick = function(){
//                modal.style.display = "block";
//                modalImg.src = this.src;
//                captionText.innerHTML = this.alt;
//            }
        }
           
    };
  });
