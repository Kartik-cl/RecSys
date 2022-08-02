
# coding: utf-8

# In[16]:


from pyspark.sql import SparkSession
import numpy as np
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import PCA
from pyspark.mllib.linalg import *
from pyspark.ml.linalg import Vectors, VectorUDT,SparseVector
from numpy.linalg import eigh
from pyspark.sql import SQLContext
from pyspark.sql import Row
from pyspark.mllib.linalg import DenseVector as DV_mllib
from pyspark.mllib.linalg import SparseVector as SV_mllib
from pyspark.mllib.linalg.distributed import RowMatrix, IndexedRowMatrix, BlockMatrix, IndexedRow
from pyspark.sql.functions import monotonically_increasing_id
import math
import itertools
import numpy as np
import random
import time
from collections import defaultdict
from scipy import sparse
from itertools import starmap,combinations
from collections import Counter
import datetime
from pyspark.ml.linalg import SparseVector, DenseVector
from random import gauss
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType
from sklearn.metrics.pairwise import cosine_similarity
import configparser as cp
from pyspark.sql.functions import udf
import pandas as pd
from six.moves.urllib.request import urlopen
import time
import requests
from pymongo import MongoClient
from scipy import spatial
from pyspark import StorageLevel
import pickle
import sys
from pyspark import SparkFiles

spark = SparkSession.builder.appName("MyApp").getOrCreate()


###########reading the configuration file and parameters###########
configpath = sys.argv[1]
# config = cp.ConfigParser()
# config.read(configpath)
spark.sparkContext.addFile(configpath)
configFile = SparkFiles.get(configpath)
config = cp.RawConfigParser()
config.read(configFile)
bucket_length =  float(config.get('BUCKET_LENGTH', 'bucket_length')) #this value can be changed from the config file
red_data_path = config.get('REDUCED_DATASET','red_dataset_path_daily_data')
neigh_info_path = sys.argv[2] #this is where the LSH output is stored. 
rv_path = sys.argv[3]
hash_lists_dict_path = config.get('HASH_LISTS_DICT_PATH', 'hash_lists_dict_path')
list_of_random_vectors = spark.sparkContext.pickleFile(rv_path, 3).collect()
hash_lists_dict = {}
for i in range(1,3): #hardcoded as of now, will change
    hash_lists_dict[i] = spark.read.format('parquet').load(hash_lists_dict_path + str(i)) 
cust_dna = spark.read.format('parquet').load(red_data_path)
num_dims = len(cust_dna.rdd.take(1)[0][1]) #takes the number of dimensions from the first column, don't like this approach :(




###########reading the configuration file and parameters###########


#global functions
def get_hash_value(densV,rand_vect):#bucket length value will be taken from the config file
    vect_in_np=densV.values
    hash_val=math.floor((vect_in_np.dot(rand_vect))/bucket_length)
    return hash_val

### This piece needs to be made configurable via lists - nothing worked !!
split1_udf = udf(lambda value: value[0].item(), FloatType())
split2_udf = udf(lambda value: value[1].item(), FloatType())
#split3_udf = udf(lambda value: value[2].item(), FloatType())
#split4_udf = udf(lambda value: value[3].item(), FloatType())
# split5_udf = udf(lambda value: value[4].item(), FloatType())
# split6_udf = udf(lambda value: value[5].item(), FloatType())
# split7_udf = udf(lambda value: value[6].item(), FloatType())
# split8_udf = udf(lambda value: value[7].item(), FloatType())

def get_neighbours(x):
    neigbours = []
    for i in range(len(x)):          
        neigbours.append([x[i],x])      
    return neigbours

def union_all(dfs):
    if len(dfs) > 1:
        return dfs[0].unionAll(union_all(dfs[1:]))
    else:
        return dfs[0]
    
    
class LSH:
    def cust_dna_hashed(self,cust_dna_rdd):
        cust_dna_hash_rdd=\
        (cust_dna_rdd
        .map(lambda x:(x[0],Vectors.dense([get_hash_value(x['pca_features'],rv) for rv in list_of_random_vectors]))))
        #.zip(cust_ids)
        #.map(lambda x : (x[1][0],x[0])))

        cust_dna_hash = spark.createDataFrame(cust_dna_hash_rdd, ["id","hashValues"])
        #self.cust_dna_hash_splitted(cust_dna_hash)
        return cust_dna_hash, list_of_random_vectors
    
    def cust_dna_hash_splitted(self,cust_dna_hash):
        cust_dna_hash_split=\
        (cust_dna_hash
        # .select(*[ udf_function_list[i]("hashValues").alias(column_names[2+i]) for i in range(num_iters)]) # This did not work :-(
        .withColumn('h1',split1_udf('hashValues'))
        .withColumn('h2',split2_udf('hashValues')))
        #.withColumn('h3',split3_udf('hashValues'))
        #.withColumn('h4',split4_udf('hashValues')))
        # .withColumn('h5',split5_udf('hashValues'))
        # .withColumn('h6',split6_udf('hashValues'))
        # .withColumn('h7',split7_udf('hashValues'))
        # .withColumn('h8',split8_udf('hashValues')))
        return cust_dna_hash_split
     
    def hashlistsdict(self,cust_dna_hash_split):
        hash_lists_dict_test={}
        for i in range(1,3):
            h_val='h'+str(i)
            target_column='list_of_rows_h'+str(i)
            this_grouped=cust_dna_hash_split.groupby(h_val).agg(F.collect_list("id").alias(target_column))
            hash_lists_dict_test[i]=this_grouped
        return hash_lists_dict_test
        
    def jointhashlistsdict(self, hash_lists_dict, hash_lists_dict_test):
        joint_hash_lists_dict = {}
        for i in range(1,len(list(hash_lists_dict.keys()))+1):
            df1 = hash_lists_dict[i]
            df2 = hash_lists_dict_test[i]
            joint_hash_lists_dict[i] = df1.join(df2, df1['h'+str(i)] == df2['h'+str(i)], 'inner').select(df1['h'+str(i)],df1['list_of_rows_h'+str(i)],df2['list_of_rows_h'+str(i)])
        return joint_hash_lists_dict
    
    def paircounts(self, joint_hash_lists_dict):
        neighbours_dict={}
        for i in range(1,len(list(hash_lists_dict.keys()))+1):
            temp_list_of_tuples=\
            (joint_hash_lists_dict[i].rdd
             .map(lambda x:(x[1]+x[2]))
             .map(lambda x: get_neighbours(x)) 
             .flatMap(lambda x:x)
             .map(lambda x:[(x[0],x[1][i]) for i in range(len(x[1]))])
             .flatMap(lambda x:x)
             .filter(lambda x: (x[0]!=x[1]))).toDF(['cust_sim_from','cust_sim_to'])
            neighbours_dict[i]=temp_list_of_tuples
            neighbours_dict[i].persist()
        all_pair_together=union_all(list(neighbours_dict.values()))
        all_pair_together.persist()
        pair_counts=all_pair_together.groupby(['cust_sim_from','cust_sim_to']).agg(F.count(F.lit(1)).alias('no_of_collision'))
        pair_counts.persist()
        return pair_counts
    
    
    
    
    

    
    
# configpath = '/data/usr/RecommendationEngine/batch/CustomerSimilarity/config/config_indexed.ini'
# config = cp.ConfigParser()
# config.read(configpath)


lsh = LSH()
cust_dna_hash,list_of_random_vectors = lsh.cust_dna_hashed(cust_dna.rdd)
cust_dna_hash_split = lsh.cust_dna_hash_splitted(cust_dna_hash)
hash_lists_dict_test= lsh.hashlistsdict(cust_dna_hash_split)
joint_hash_lists_dict = lsh.jointhashlistsdict(hash_lists_dict,hash_lists_dict_test)
pair_counts = lsh.paircounts(joint_hash_lists_dict)
pair_counts.write.save(neigh_info_path, mode = 'overwrite')
