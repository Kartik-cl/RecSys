# coding: utf-8

'''
This piece of code takes in the reduced product dna and gives out the pairs of customers similar to each other. The algorithm used to find the same is locality sensitive hashing(LSH). It takes
a probabilistic approach to find the neighbors of the customers so that the similarity is needed to find between these neighbors only. This is done since it is infeasible to calculate similarities
between all customers in a larger dataset
'''

#############start of all the imports ##################
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
import ConfigParser as cp
from pyspark.sql.functions import udf
import pandas as pd
from six.moves.urllib.request import urlopen
import time
import requests
from scipy import spatial
from pyspark import StorageLevel
import pickle
import sys
from pyspark import SparkFiles
############# end of all the imports ##################

#defining the spark variable in order to get the spark SQL and sparkcontext capabilities
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
red_data_path = config.get('REDUCED_DATASET', 'red_dataset_path') #this is the reduced dataset from PCA                                                    
neigh_info_path = sys.argv[2] #config.get('NEIGHBOURS', 'neigh_info_path') #this is where the LSH output is stored. 
rv_path = sys.argv[3]
###########reading the configuration file and parameters###########

cust_dna = spark.read.format('parquet').load(red_data_path) #reading the PCA output

num_dims = len(cust_dna.rdd.take(1)[0][1]) #takes the number of dimensions from the first column



############# start of global funtions ##################

#takes customer indexes as input and returns their similarity
def get_similarity(cust_dna_dict,cus_index1,cus_index2):
    vec1 = cust_dna_dict[cus_index1]
    vec2 = cust_dna_dict[cus_index2]
    similarity = cosine_similarity(vec1,vec2)[0][0]
    return str(similarity)
            
#takes a customer data point and maps it to a hash value
def get_hash_value(densV,rand_vect):
    vect_in_np=densV.values
    hash_val=math.floor((vect_in_np.dot(rand_vect))/bucket_length)
    return hash_val

def make_rand_vector(num_dims):
        vec = [gauss(0, 1) for i in range(num_dims)]
        mag = sum(x**2 for x in vec) ** .5
        return [x/mag for x in vec]

### This piece needs to be made configurable via lists - nothing worked !!
split1_udf = udf(lambda value: value[0].item(), FloatType())
split2_udf = udf(lambda value: value[1].item(), FloatType())
#split3_udf = udf(lambda value: value[2].item(), FloatType())
#split4_udf = udf(lambda value: value[3].item(), FloatType())
# split5_udf = udf(lambda value: value[4].item(), FloatType())
# split6_udf = udf(lambda value: value[5].item(), FloatType())
# split7_udf = udf(lambda value: value[6].item(), FloatType())
# split8_udf = udf(lambda value: value[7].item(), FloatType())

def union_all(dfs):
    if len(dfs) > 1:
        return dfs[0].unionAll(union_all(dfs[1:]))
    else:
        return dfs[0]
    
def get_neighbours(x):
    neigbours = []
    for i in range(len(x)):          
        neigbours.append([x[i],x])      
    return neigbours

#############end of global funtions ##################


'''
This LSH class takes the reduced product dna and finds out the nearest neighbors for the customers.
It hashes each customer. This process of hashing each customer is done a certain number of times.
All customers hashing to the same value at all iterations are considered as neighbors.
'''
class LSH:
    #constructor declaration initial configuration
    def __init__(self,num_iters,bucket_length,num_dims,configpath):
        self.num_iters = num_iters
        self.bucket_length = bucket_length
        self.num_dims = num_dims
        self.rv_path = config.get('RANDOM_VECS_PATH','random_vec_path')
        self.hash_lists_dict_path = config.get('HASH_LISTS_DICT_PATH','hash_lists_dict_path')
        self.hash_lists_dict = {}
    
    #generates and returns random vectors with dimensions equal to the reduced customer dna
    def rand_vec_list(self):
        list_of_random_vectors=[make_rand_vector(self.num_dims) for i in range(self.num_iters)]
        spark.sparkContext.parallelize(list_of_random_vectors).saveAsPickleFile(rv_path)
        return list_of_random_vectors
    
    #returns the hashed dataframe with customer index and its hash value
    def cust_dna_hashed(self,cust_dna):
        '''
        sample example
        The input of this function is of the following format:
        Row(id = 1234, pca_features = DenseVector([0.4494, -0.6573, 0.1983 ... ]))
        Row(id = 5678, pca_features = DenseVector([0.4521, -0.2453, -0.2922 ... ]))
        
        The output of this function is in the following format:
        +------+-----------+
        |    id| hashValues|
        +------+-----------+
        |1234  | [-4.0,0.0]|
        |5678  | [3.0,-1.0]|
        .
        .
        .
        
        '''

        cust_dna_rdd = cust_dna.rdd
        list_of_random_vectors = self.rand_vec_list()
        cust_dna_hash_rdd=        (cust_dna_rdd
        .map(lambda x:(x[0],Vectors.dense([get_hash_value(x['pca_features'],rv) for rv in list_of_random_vectors]))))

        cust_dna_hash = spark.createDataFrame(cust_dna_hash_rdd, ["id","hashValues"])
        return cust_dna_hash, list_of_random_vectors
    
    
    def cust_dna_hash_splitted(self,cust_dna_hash):
        '''
        The input of this function is:
        +------+-----------+
        |    id| hashValues|
        +------+-----------+
        |1234  | [-4.0,0.0]|
        |5678  | [3.0,-1.0]|
        .
        .
        .
        
        The output of this function is in the following format:
        +------+-----------+----+----+
        |    id| hashValues|  h1|  h2|
        +------+-----------+----+----+
        |1234   | [-4.0,0.0]|-4.0| 0.0|
        |5678   | [3.0,-1.0]| 3.0|-1.0|
        .
        .
        .

        '''
        cust_dna_hash_split=        (cust_dna_hash
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
        '''
        The input of this function is in the following format:
        +------+-----------+----+----+
        |    id| hashValues|  h1|  h2|
        +------+-----------+----+----+
        |1234   | [-4.0,0.0]|-4.0| 0.0|
        |5678   | [3.0,-1.0]| 3.0|-1.0|
        .
        .
        .

        The output of this function is a dict of dataframes:
        +-----+--------------------+
        |   h1|     list_of_rows_h1|
        +-----+--------------------+
        |  9.0|[1162379, 777885,...|
        |-11.0|[1143365, 1068767...|
        |  5.0|[159954, 504026, ...|
        |-17.0|            [111947]|
        | -9.0|[640495, 1165546,...|

        +-----+--------------------+
        |   h2|     list_of_rows_h2|
        +-----+--------------------+
        | 18.0|    [106817, 527529]|
        |  9.0|[186200, 192920, ...|
        |-11.0|           [1023003]|
        |  5.0|[826556, 640591, ...|
        | 17.0|    [622199, 469541]|

        '''
        hash_lists_dict={}
        for i in range(1,self.num_iters+1):
            h_val='h'+str(i)
            target_column='list_of_rows_h'+str(i)
            this_grouped=cust_dna_hash_split.groupby(h_val).agg(F.collect_list("id").alias(target_column))
            hash_lists_dict[i]=this_grouped
        return hash_lists_dict
        
    #returns the number of times a pair of customers have come across as similar
    def paircounts(self,hash_lists_dict):
        neighbours_dict={}
        for i in range(1,len(list(hash_lists_dict.keys()))+1):
            temp_list_of_tuples=            (hash_lists_dict[i]
             .rdd
             .map(lambda x:(x[1]))
             .map(lambda x: get_neighbours(x))  
             .flatMap(lambda x:x)
             .map(lambda x:[(x[0],x[1][i]) for i in range(len(x[1]))])
             .flatMap(lambda x:x)
            ).toDF(['cust_sim_from','cust_sim_to'])
            neighbours_dict[i]=temp_list_of_tuples
            neighbours_dict[i].persist()
        all_pair_together=union_all(list(neighbours_dict.values()))
        all_pair_together.persist()
        pair_counts=all_pair_together.groupby(['cust_sim_from','cust_sim_to']).agg(F.count(F.lit(1)).alias('no_of_collision'))
        pair_counts.persist()
        return pair_counts
    
    #writes out the random vectors and hash list dict
    def write_out(self,hash_lists_dict, random_vecs):
        # with open(self.rv_path, 'wb') as f:
        #     pickle.dump(random_vecs, f ,protocol = 2)
            
        for i in range(1,len(list(hash_lists_dict.keys()))+1):
            hash_lists_dict[i] = hash_lists_dict[i].write.save(self.hash_lists_dict_path + str(i), mode = 'overwrite')
            
    #filters and returns pairs with maximum possible collisions
    def filter_collisions(self, pair_counts):
        pair_counts = (pair_counts
                       .filter('no_of_collision>1')
                      )
        return pair_counts
        

        
        



lsh = LSH(2,bucket_length,num_dims,configpath) # creating an instance of the LSH class

#calling the necessary functions from the LSH class
cust_dna_hash, random_vecs = lsh.cust_dna_hashed(cust_dna)
cust_dna_hash_split = lsh.cust_dna_hash_splitted(cust_dna_hash)
hash_lists_dict= lsh.hashlistsdict(cust_dna_hash_split)
pair_counts = lsh.paircounts(hash_lists_dict)
#pair_counts = lsh.filter_collisions(pair_counts)
lsh.write_out(hash_lists_dict, random_vecs)
pair_counts.write.save(neigh_info_path)


