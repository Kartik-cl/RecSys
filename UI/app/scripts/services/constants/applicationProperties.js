'use strict';

angular.module('watsonRetailApp')
    .constant('applicationProperties', {
        CONTEXT_ATTR_VIEW_RELATED_PRODUCT: "viewRelatedProduct",
        CONTEXT_ATTR_PURCHASE: "purchase",
        CONTEXT_ATTR_VALUE_YES:"yes",
        CONTEXT_ATTR_VALUE_NO:"no",
        UI_CONTEXT_ATTR_RECOMMEND:"recommendations",
        UI_CONTEXT_ATTR_STYLE_RECOMMEND:"styleRecommend",
        IS_SHOW_MORE_ATTR:"isShowMoreProducts",
        IS_VIEW_RELATED_PRODUCTS_ATTR:"isViewRelatedProducts",
        SHOW_LIST_ATTR:"showList",
        WATSON_TYPING_ATTR:"watsonTyping",
        USER_TYPING_ATTR:"userTyping",
        WATSON: "watson",
        USER: "user"
    });
