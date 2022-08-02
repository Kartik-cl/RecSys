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

EPOCHS = 5
BATCH_SIZE =256
N_BATCHES = int(ratings.shape[0]/BATCH_SIZE)

for epoc in range(EPOCHS):
    for i in range(N_BATCHES):
        startIndex = i*BATCH_SIZE
        endIndex = BATCH_SIZE*(i+1) if BATCH_SIZE*(i+1) < ratings.shape[0] else ratings.shape[0]-1
        batch_ratings = ratings.loc[startIndex:endIndex]
        batch_userIds = batch_ratings['userId'].unique()
        batch_prodIds = batch_ratings['productId'].unique()
        
        map_user_id_to_index = dict(zip(batch_userIds,range(len(batch_userIds))))
        map_prod_id_to_index = dict(zip(batch_prodIds,range(len(batch_prodIds))))
        
        
        batch_ratings_mat = pd.DataFrame(np.zeros((len(batch_userIds),len(batch_prodIds))))
        for row_index in range(startIndex,endIndex):
            userindex = map_user_id_to_index[batch_ratings.loc[row_index]['userId']]
            prodindex = map_prod_id_to_index[batch_ratings.loc[row_index]['productId']]
            batch_ratings_mat.loc[userindex][prodindex] = batch_ratings.loc[row_index]['rating']
    
        batch_user = usertrain.loc[batch_userIds].values
        batch_item_txt = prod_txt_inp.loc[batch_prodIds].values
        batch_item_img = prod_img_inp.loc[batch_prodIds].values
        #print(len(batch_user),len(batch_item_txt),len(batch_item_img))
        dae.train_model(sess,batch_user,batch_item_txt,batch_item_img,batch_ratings_mat.values)
        if i%100 == 0 or i==N_BATCHES-1:
            dae.test_model(sess,batch_user,batch_item_txt,batch_item_img)
            err = dae.validate_model(sess,batch_user,batch_item_txt,batch_item_img,batch_ratings_mat.values)
            print(epoc,i,err)
            dae.save_weights(sess)
