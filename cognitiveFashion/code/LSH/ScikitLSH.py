# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 09:54:09 2018

@author: ibm_admin
"""

import pickle
from sklearn.neighbors import LSHForest

import ssl
import base64
import pymongo

import time

class LSH:
    def __init__(self):
        print('Inside LSH class')
        self.MONGODB_URL = 'mongodb://admin:YFIQRJASNZOUHBWA@portal-ssl1937-1.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628,portal-ssl1547-29.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628/compose?authSource=admin&ssl=true'
        self.client = pymongo.MongoClient(self.MONGODB_URL, ssl_cert_reqs=ssl.CERT_NONE)
        self.collection = self.client.compose.temp_product_thumbnail_image
        
    def getPickle(self, c_name):
        pkl_location = 'pklData/' + c_name + '_features.pkl'
        file = open(pkl_location, 'rb')
        pkl_data = pickle.load(file)
        return pkl_data
        
    def generateResult(self,result, pkl_data, c_name, outfit):
        final_json = {}
        final_result = []
        if c_name == 'None':
            final_json['product_id'] = outfit['product_id']
            final_json['image_URI'] = base64.b64encode(outfit['embedding']['image_feat'])
            final_json['product_name'] = outfit['product_name'] 
            final_json['type_of_category'] = outfit['type_of_category']
            final_result.append(final_json)
            outfit['in_product_inventory'] = 'N'
            outfit['similar_products'] = final_result
            outfit.pop('embedding')
            return outfit
        else:
            keys = list(pkl_data.keys())
            for t in sorted(result.items(), key = lambda x : x[1]):
                final_json['product_id'] = pkl_data[keys[t[0]]]['product_id']
                cursor = self.collection.find({ 'productId' : pkl_data[keys[t[0]]]['product_id']})
                uri = list(map(lambda document : document['thumbnail'], cursor))
                final_json['image_URI'] = uri[0][uri[0].index('/9j') : uri[0].index('">')]
                final_json['product_name'] =  keys[t[0]].split('/')[1]
                final_json['type_of_category'] = pkl_data[keys[t[0]]]['category_name']
                final_result.append(final_json.copy())
            outfit['in_product_inventory'] = 'Y'
            outfit['similar_products'] = final_result
            outfit.pop('embedding')
            return outfit
        
    def lshProcessing(self,c_name, q_vector, outfit):
        X_train = []
        lsh_result = {}
        pkl_data = self.getPickle(c_name) 
        for key,value in pkl_data.items():
            X_train.append(value['image_rnn_feat']) 
        X_test = q_vector.reshape(1,-1)
        #fit the LSH Forest on the data
        #random_state is the seed used by the random number generator
        #min_hash_match : Lowest hash length to be searched when candidate selection is performed for nearest leighbors
        #n_candidates : Minimum number of candidates evaluated per estimator, assuming enough items meet the min_hash_match constraint
        #n_neighbours : Number of neighbors to be returned from query function when it is not provided to the kneighbors method
        lshf = LSHForest(min_hash_match = 5, n_candidates = 55, random_state = 42)
        lshf.fit(X_train)
        distances, indices = lshf.kneighbors(X_test, n_neighbors = 10)
        distances, indices = [item for sublist in distances for item in sublist], [item for sublist in indices for item in sublist]
        for i,d in enumerate(distances):
            lsh_result[indices[i]] = distances[i]
        return lsh_result, pkl_data

    def getData(self,data):
        final_output = {}
        final_output['conversation_id'] = data['conversation_id']
        final_output['selected_product_id'] = data['selected_product_id']
        final_output['selected_product_image_URI'] = data['selected_product_image_URI']
        final_output['outfit_details'] = []
        start = time.clock()
        for outfit in data['outfit details']:
            c_name, q_vector  = outfit['type_of_category'], outfit['embedding']['image_rnn_feat']
            if c_name == 'None':
                final_output['outfit_details'].append(self.generateResult(None, None, c_name, outfit))
            else:
                lsh_result, pkl_data = self.lshProcessing(c_name, q_vector, outfit)
                final_output['outfit_details'].append(self.generateResult(lsh_result, pkl_data, c_name, outfit))
        print(time.clock() - start)
        return (str(final_output).replace("u'", "'"))