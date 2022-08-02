# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 12:15:09 2018

@author: Sapna
"""

from __future__ import print_function
import numpy as np
import tensorflow as tf
import pandas as pd
from scipy import sparse
import json
import DLRecommendationEngine
import pickle
import os
import numpy as np
dataPath = '../data/'



''' Fetching Prod Image Input '''
folder = '../data/pklData/'
files = os.listdir(folder)

map_prodid_to_index = {}
count=0
img_inp = []
img_inp_pid = []
sum = 0
for f in files :
    with open(folder+f,'rb') as file:
        prod_img_raw = pickle.load(file,encoding='bytes')
    prod_img_raw = list(prod_img_raw.values())
    sum+=len(prod_img_raw)
    #print(f,len(prod_img_raw))
    for prod_img in prod_img_raw:
        map_prodid_to_index[prod_img[b'product_id']]=count
        count+=1
        img_inp_pid.append(prod_img[b'product_id'])
        img_inp.append(prod_img[b'image_feat'])

prod_img_inp = np.array(img_inp)
prod_img_inp = pd.DataFrame(prod_img_inp,index=img_inp_pid)


prod_txt_inp_path = dataPath + 'final_product_dna.csv'
prod_txt_inp = pd.read_csv(prod_txt_inp_path)
prod_ids = prod_txt_inp['productId']
prod_txt_inp.set_index('productId',inplace=True)
prod_txt_inp = prod_txt_inp.loc[prod_txt_inp.index.isin(map_prodid_to_index.keys())]

userpath = dataPath + 'customer_dna.json'
with open(userpath, 'r') as infile:
    usertrain = json.load(infile)
usertrain = pd.DataFrame.from_dict(usertrain, orient='columns')
usertrain.set_index('userId',inplace=True)

ratingpath = dataPath+'utility.csv'
ratings = pd.read_csv(ratingpath)
ratings = ratings[['userId',  'productId',  'rating']]
val_ratings = ratings.loc[:200].reset_index(drop=True)
ratings = ratings.loc[200:500000].reset_index(drop=True)
np.savetxt("../data/test/rating_actual.csv", val_ratings.values, delimiter=",")


dae = DLRecommendationEngine.RecomendationEngine([20,50],[855,100,50],[512,100,50],0.2,0.3)
sess = tf.Session()
dae.init_session(sess)
dae.restore_model(sess)

EPOCHS = 1
BATCH_SIZE =256
N_BATCHES = int(ratings.shape[0]/BATCH_SIZE) + 1

prod_encoding_arr = np.zeros([len(prod_ids),50])

for epoc in range(EPOCHS):
    for i in range(N_BATCHES):
        startIndex = i*BATCH_SIZE
        endIndex = BATCH_SIZE*(i+1) if BATCH_SIZE*(i+1) < prod_txt_inp.shape[0] else prod_txt_inp.shape[0]-1
        batch_prodIds = prod_ids.loc[startIndex:endIndex]
        batch_item_txt = prod_txt_inp.loc[batch_prodIds].values
        batch_item_img = prod_img_inp.loc[batch_prodIds].values
        
        arr = sess.run(dae.prod_embeddings, feed_dict={dae.ph_prod_txt_inp:batch_item_txt,dae.ph_prod_img_inp:batch_item_img})
        print(arr.shape)
        prod_encoding_arr[startIndex:endIndex+1,:] = arr
        
print(prod_encoding_arr.shape)
np.savetxt("../data/all_prod_embeddings.csv", prod_encoding_arr, delimiter=",")