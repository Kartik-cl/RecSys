# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 02:09:08 2018

@author: Kartikeya
"""

import filter
import time
from flask import Flask
import json
from flask import request
from os import environ
import os
from pymongo import MongoClient
from bson.json_util import dumps
import pymongo
from collections import defaultdict
from itertools import chain
import numpy as np
#flask app



app = Flask(__name__)


os.environ['MONGODB_URL'] = "mongodb://admin:YFIQRJASNZOUHBWA@portal-ssl1937-1.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628,portal-ssl1547-29.bmix-dal-yp-1c122420-8676-4ab7-963e-be4fad7d17a8.1922556651.composedb.com:54628/compose?authSource=admin&ssl=true"
MONGODB_URL = os.environ.get('MONGODB_URL')
client = pymongo.MongoClient(MONGODB_URL)
db = client.get_database()
prod_coll = db['product_dna_encoded_updated_2']
img_coll = db['temp_product_thumbnail_image']
collector = defaultdict(dict)


def mongoRequest(context):
#    query_set = [{'product_index' : 95004}, {'product_index' : 85853}]
    cursor = prod_coll.find({"$or":context})
    candidate_set = json.loads(dumps(cursor))
    return candidate_set

def innerJoin(fil_selected, images_rec):
    print(images_rec[0].keys())
    for collectible in chain(fil_selected, images_rec):
        collector[collectible['product_index']].update(collectible.items())

    recommendation_set = list(collector.values())
    return recommendation_set


@app.route('/recallRec')
def api_recall():
    if request.method == 'GET':
        context = eval(request.args.get("context"))
        for d in context:
            if 'userId' in d.keys():
                userId = d['userId']
#        userId = [d['userId'] if 'userId' in d.keys() for d in context]
#        print("userId is: ")
#        print(userId)
        fil = mongoRequest(context)
        try:    
            predict_scores, fil = ra.recResults(None, fil, int(userId))
        except:
            predict_scores, fil = ra.recResults(None, fil, None)
        top_prod_indexes = np.argsort(predict_scores[0][0])[::-1][:8]
        print(top_prod_indexes)
        fil_selected = [fil[i] for i in top_prod_indexes]
        fil_selected_indexes = [fil[i]['product_index'] for i in top_prod_indexes]
        get_img_query = []
        for i in range(len(fil_selected)):
            get_img_query.append({'productId' : fil_selected[i]['product_index']})
        cursor = img_coll.find({"$or":get_img_query})
        images_rec = json.loads(dumps(cursor))
        for i in range(len(images_rec)):   
            images_rec[i]['product_index'] = images_rec[i].pop('productId')
        recommendation_set = innerJoin(images_rec, fil_selected)
        recommendation_set_ordered = [(item for item in recommendation_set if item['product_index'] == i).__next__() for i in fil_selected_indexes]
        response = [{'product_index' : recommendation_set_ordered[i]['product_index'],'product_name' : recommendation_set_ordered[i]['image_location'][recommendation_set_ordered[i]['image_location'].find('/') + 1:recommendation_set_ordered[i]['image_location'].find('.jpg')].replace("_", " ").replace("-", " ").replace("/", "_"), 'img_src' : recommendation_set_ordered[i]['thumbnail'][recommendation_set_ordered[i]['thumbnail'].find('src') + 5:-2]} for i in range(len(recommendation_set_ordered))]
        return json.dumps(response)
        


@app.route('/')
def api_call():
#    context = {'product' : 'Blouse'}
    if request.method == 'GET':
        context = eval(request.args.get("context"))
        if 'userId' in context.keys():    
            predict_scores, fil = ra.recResults(context, None, int(context['userId']))
        else:
            predict_scores, fil = ra.recResults(context, None, None)
#        predict_scores, fil = ra.recResults(context)
        print(predict_scores[0][0])
        print(type(predict_scores))
        top_prod_indexes = np.argsort(predict_scores[0][0])[::-1][:8]
        print(top_prod_indexes)
        fil_selected = [fil[i] for i in top_prod_indexes]
        fil_selected_indexes = [fil[i]['product_index'] for i in top_prod_indexes]
        get_img_query = []
        for i in range(len(fil_selected)):
            get_img_query.append({'productId' : fil_selected[i]['product_index']})
        cursor = img_coll.find({"$or":get_img_query})
        images_rec = json.loads(dumps(cursor))
        for i in range(len(images_rec)):   
            images_rec[i]['product_index'] = images_rec[i].pop('productId')
        recommendation_set = innerJoin(images_rec, fil_selected)
        recommendation_set_ordered = [(item for item in recommendation_set if item['product_index'] == i).__next__() for i in fil_selected_indexes]
        response = [{'product_index' : recommendation_set_ordered[i]['product_index'],'product_name' : recommendation_set_ordered[i]['image_location'][recommendation_set_ordered[i]['image_location'].find('/') + 1:recommendation_set_ordered[i]['image_location'].find('.jpg')].replace("_", " ").replace("-", " ").replace("/", "_"), 'img_src' : recommendation_set_ordered[i]['thumbnail'][recommendation_set_ordered[i]['thumbnail'].find('src') + 5:-2]} for i in range(len(recommendation_set_ordered))]
        return json.dumps(response)
    

if __name__ == "__main__":
    ra = filter.recAPI()
    HOST = environ.get('VCAP_APP_HOST', 'localhost')
    try:
        PORT = int(environ.get('PORT', '8000'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug = True)