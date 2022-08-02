# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 18:42:44 2018

@author: Kartikeya
"""

import json
import random
from flask import Flask
from flask import request
#from os import environ
import pymongo
import numpy as np
import DLRecommendationEngine
import tensorflow as tf
import os
import time
from bson.json_util import dumps
import pickle

os.environ['MONGODB_URL'] = "mongodb://admin:YFIQRJASNZOUHBWA@portal-ssl1937-1.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628,portal-ssl1547-29.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628/compose?authSource=admin&ssl=true"

class recAPI:
    def __init__(self):
            self.MONGODB_URL = os.environ.get('MONGODB_URL')
            self.client = pymongo.MongoClient(self.MONGODB_URL)
            self.db = self.client.get_database()
            self.prod_coll = self.readprodDNA()
            self.cust_coll = self.readcustDNA()
            cust_dim, prod_dim = self.getDimensions()
            self.rec_object = DLRecommendationEngine.RecomendationEngine([20,50], [855,100,50],[512,100,50],0.2,0.3)
            self.sess = tf.Session()
            self.rec_object.restore_model(self.sess)
            pass
        
        
    def getDimensions(self):
        cust_dim = len(self.cust_coll.find_one().keys()) - 2  #hardcoed length
        prod_dim = 855 #len(self.prod_coll.find_one()['hot_encoding'])
        return cust_dim, prod_dim
    
    def readprodDNA(self):
        collection_name = 'product_dna_encoded_updated_2'
        prod_coll = self.db[collection_name]
        return prod_coll
    
    def readcustDNA(self):
        collection_name = 'customer_dna_encoded'
        cust_coll = self.db[collection_name]
        return cust_coll
    
        
    
    def filteredData(self, context):
        print(type(context))
        d = context['attributes']
        l = list(d.items())
        search_query = [{'attributes.' + l[i][0] : l[i][1]} for i in range(len(l))]
        print("the search query is: ")
        print(search_query)
        cursor = self.prod_coll.find({"$and":search_query})
        fil = json.loads(dumps(cursor))
        hot_encoding_matrix = np.zeros([len(fil),855])
        image_features = []
        ind=0
#        print(fil)
        for item in fil:
            encoding_index = item['dna_feat']
            np.put(hot_encoding_matrix[ind], encoding_index, np.ones(len(encoding_index)))
            image_features.append(eval(item['image_feat']))
            ind+=1
#        np.savetxt('hot_encoding_matrix.csv', hot_encoding_matrix, delimiter = ',')
        
        return hot_encoding_matrix, np.array(image_features), fil
    
    def prefilteredData(self, fil):
        hot_encoding_matrix = np.zeros([len(fil),855])
        image_features = []
        ind=0
        for item in fil:
            encoding_index = item['dna_feat']
            np.put(hot_encoding_matrix[ind], encoding_index, np.ones(len(encoding_index)))
            image_features.append(eval(item['image_feat']))
            ind+=1
#        np.savetxt('hot_encoding_matrix.csv', hot_encoding_matrix, delimiter = ',')
#        print("image features: ")
#        print(image_features)
        return hot_encoding_matrix, np.array(image_features), fil
        
    
    def getCustomerData(self, userId = None):    #later based on user login add context as parameter
        if userId is None:    
            cursor = self.cust_coll.find({'userId':70998})
        else:
            cursor = self.cust_coll.find({'userId':userId})
        for rec in cursor:
            record = rec
        del(record['_id'])
        del(record['userId'])
        return np.fromiter(record.values(), dtype=int).reshape([1,20])
    
    def predict(self,user,prod,image):
#        rec_object = DLRecommendationEngine.RecomendationEngine(user.shape[1],100,50,prod.shape[1],400,200,50)
#             self.rec_object.restore_model(sess)
        pred_mat = self.rec_object.test_model(self.sess,user,prod,image)
        #sess.close()
        #del(rec_object)
        return pred_mat

    def recResults(self, context = None, fil = None, userId = None):
#        context = {'attributes': {'look': 'light', 'product': 'Blazer'}}
        if context is not None:    
            prod_mat_encoded, image_features_encoded, fil = self.filteredData(context)
        if fil is not None:
            prod_mat_encoded, image_features_encoded, fil = self.prefilteredData(fil)
        if userId is not None:
            res_customer_mat = self.getCustomerData(userId)
        if userId is None:
            res_customer_mat = self.getCustomerData()
        product_scores = self.predict(res_customer_mat, prod_mat_encoded, image_features_encoded)
        return product_scores, fil

#    def recResults(self, fil):
#        prod_mat_encoded, fil = self.prefilteredData(fil)
#        res_customer_mat = self.getCustomerData()
#        product_scores = self.predict(res_customer_mat,prod_mat_encoded)
#        return product_scores, fil

#start_time = time.time()     
#ra = recAPI()
#context = {'attributes': {'look': 'light', 'product': 'Blazer'}}
#prod_mat_encoded = ra.filteredData(context)
##print(time.time() - start_time)
##start_time = time.time()
#res_customer_mat = ra.getCustomerData()
##print(time.time() - start_time)
##start_time = time.time()
#product_scores = ra.predict(res_customer_mat,prod_mat_encoded)
#print(time.time() - start_time)
#print(product_scores)
#
