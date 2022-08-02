from __future__ import print_function
import numpy as np
import pandas as pd
from scipy import sparse
import json
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
prod_img_data = []
for f in files :
    with open(folder+f,'rb') as file:
        prod_img_raw = pickle.load(file,encoding='bytes')
    prod_img_raw = list(prod_img_raw.values())
    sum+=len(prod_img_raw)
    for prod_img in prod_img_raw:
        map_prodid_to_index[prod_img[b'product_id']]=count
        count+=1
        img_inp_pid.append(prod_img[b'product_id'])
        img_inp.append(prod_img[b'image_feat'])
        prod_info = {}
        prod_info['productId'] = prod_img[b'product_id']
        
        prod_info['image_feat'] = pd.Series(prod_img[b'image_feat']).to_json(orient='values')
        prod_img_data.append(prod_info)

prod_img_data_json = json.dumps(prod_img_data)

with open("../data/prod_img_data.json","w") as f:
    f.write(prod_img_data_json)

prod_txt_inp_path = dataPath + 'final_product_dna.csv'
prod_txt_inp = pd.read_csv(prod_txt_inp_path)
