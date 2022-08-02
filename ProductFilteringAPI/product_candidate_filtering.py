# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 02:56:30 2018

@author: Kartikeya
"""
import json
import itertools
from math import log2
import time
import random
from flask import Flask
from flask import request
from os import environ
from collections import Counter

#with open('C://Users//IBM_ADMIN//Desktop//graphs//product_dna.json') as f:
#     data = json.load(f)

attributes_traversed = []

class FilterDataSet:
    
    def __init__(self, data):
            self.data = data
            self.threshold = 200
    
    def filteredData(self, context):
        print(type(context))
        d = context['attributes']
        l = list(d.items())
        s= ""
        for i in range(len(l)):
            if i < len(l) - 1:
                s += '"' + l[i][1] + '"' + ' in ' + 'data[i]' + '[' + '"' + l[i][0] + '"' + ']' + " and " 
            else:
                s += '"' + l[i][1] + '"' + ' in ' + 'data[i]' + '[' + '"' + l[i][0] + '"' + ']'
                
        print(s)
        fil = []
        for i in range(len(self.data)):
            try:
                if(eval(s)):
                    fil.append(self.data[i])
            except:
                pass
        return fil
        
    
    def apiResponse(self, context):
#        context = json.loads(context)
        max_entropy_val = 0
        entropy = {}
        filtered_data = self.filteredData(context)
#        print(len(filtered_data))
        count_filtered = len(filtered_data)
        attr_names = set().union(*(d.keys() for d in filtered_data))
        for name in attr_names:
            probs = []
            temp_l = [d[name] for d in filtered_data if name in d]
            temp_l_flat = [item for sublist in temp_l for item in sublist]
            c = Counter(temp_l_flat)
            for i in c:
                probs.append(c[i] / count_filtered)
            probs.append(1-sum(probs))
            try:
                entropy_val = -sum([probs[i] * log2(probs[i]) for i in range(len(probs))])
                if(entropy_val > max_entropy_val):
                    max_entropy_val = entropy_val
                    valid_values = list(set(temp_l_flat))
                    next_attr = name
                    topn =   [i[0] for i in c.most_common(7)]
                    valid_values = list(set(valid_values) & set(topn))
                entropy[name] = entropy_val
#                print("entropy is")
#                print(entropy)
#                print("probability values are: ")
#                print(probs)
                
            except:
                pass
        
        
            
        
        print(count_filtered)
        
        if(count_filtered < self.threshold):
            context['next_attr'] = "no next attribute"
            context['next_attr_values'] = ""
        else:
            print("this condition true")
            print(count_filtered)
            context['next_attr'] = next_attr
            context['next_attr_values'] = valid_values
        return json.dumps(context)


with open('new_product_dna_updated1.json') as f:
    data = json.load(f)

data = [data[i]['attributes'] for i in range(len(data))]



#flask app
app = Flask(__name__)
@app.route('/')
def api_call():
#    context = {'product' : 'Blouse'}
    if request.method == 'GET':
        fds = FilterDataSet(data)
        context = eval(request.args.get("context"))
        print (type(request.args.get("context")))
#        print(type(context))
#        attributes = request.args.get("attributes")
#        attributes_info =  request.args.get("attributes_info")
#        context = json.loads(context)
#        context = {'attributes': {'hem': 'a-line', 'product': 'Dress'}}
#        context = json.dumps(context)
        print(type(context))
        context_response = fds.apiResponse(context)

        return context_response
#
#
if __name__ == "__main__":
    HOST = environ.get('VCAP_APP_HOST', 'localhost')
    try:
        PORT = int(environ.get('PORT', '8000'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)




