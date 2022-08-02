# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 21:52:14 2018

@author: Sapna
"""
import pickle
import json
import pandas as pd
import DLRecommendationEngine
import tensorflow as tf
import numpy as np
### import custormer data as numpy
dataPath = '../data/'

userpath = dataPath + 'customer_dna.json'
itempath = dataPath + 'product_dna_hot_encoded.json'

with open(userpath, 'r') as infile:
    usertrain = json.load(infile)

with open(itempath, 'r') as infile:
    prodtrain = json.load(infile)
    
usertrain = pd.DataFrame.from_dict(usertrain, orient='columns')
usertrain.set_index('userId',inplace=True)
#rating_mat = sparse.load_npz(ratingpath)
prodtrain =pd.DataFrame.from_dict(prodtrain, orient='columns')
prodtrain.set_index('productId',inplace=True)

ratingpath = dataPath+'utility.csv'
ratings = pd.read_csv(ratingpath) 
val_ratings = ratings[:300]
val_userIds = val_ratings['userId'].unique()
val_prodIds = val_ratings['productId'].unique()

dae_test = DLRecommendationEngine.RecomendationEngine(usertrain.shape[1],100,50,prodtrain.shape[1],400,200,50)
sess= tf.Session()
dae_test.restore_model(sess)



map_user_id_to_index = dict(zip(val_userIds,range(len(val_userIds))))
map_prod_id_to_index = dict(zip(val_prodIds,range(len(val_prodIds))))


val_ratings_mat = pd.DataFrame(np.zeros((len(val_userIds),len(val_prodIds))))
for row_index in range(len(val_ratings)):
    userindex = map_user_id_to_index[val_ratings.loc[row_index]['userId']]
    prodindex = map_prod_id_to_index[val_ratings.loc[row_index]['productId']]
    val_ratings_mat.loc[userindex][prodindex] = val_ratings.loc[row_index]['rating']

val_user = usertrain.loc[val_userIds]#.values#[:,:-1]
val_item = prodtrain.loc[val_prodIds]#.values 
val_error = dae_test.validate_and_check_early_stopping(sess,val_ratings,val_user,val_item)
print("Val error:",val_error)
dae_test.test_model(sess,usertrain.values[:2,:],prodtrain.values[:200,:])    
sess.close()