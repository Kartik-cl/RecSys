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
import sys


def get_similarity(cust_dna_dict,cus_index1,cus_index2):
    vec1 = cust_dna_dict[cus_index1]
    vec2 = cust_dna_dict[cus_index2]
    similarity = cosine_similarity(vec1,vec2)[0][0]
    return str(similarity) 


spark = SparkSession.builder.appName("MyApp").getOrCreate()


configpath = sys.argv[1]
config = cp.ConfigParser()
config.read(configpath)
red_data_path = config.get('REDUCED_DATASET','red_dataset_path')
red_data_path_daily = config.get('REDUCED_DATASET','red_dataset_path_daily_data')
neigh_info_path = sys.argv[2]
sim_out_path = sys.argv[3]


cust_dna = spark.read.format('parquet').load(red_data_path)
cust_dna_daily = spark.read.format('parquet').load(red_data_path_daily)
cust_dna = cust_dna.union(cust_dna_daily)
lsh_res = spark.read.format('parquet').load(neigh_info_path)
cust_dna_collected=(cust_dna
                    .rdd
                    .map(lambda x:(x['id'],np.array(x['pca_features'])))
                    ).collect()
cust_dna_dict= {t[0]:t[1:] for t in cust_dna_collected}

lsh_res_filtered = (lsh_res
         .rdd
         .filter(lambda x:x['no_of_collision']>=2))

disk_storage= StorageLevel(True, False, False, False, 1)
lsh_res_filtered.persist(disk_storage)

output_rdd = (lsh_res_filtered
             .map(lambda x: (x[0],x[1],get_similarity(cust_dna_dict,x[0],x[1])))
             .map(lambda x:(x[0],[x[0],'c',x[1],x[2]])))
output_rdd.saveAsTextFile(sim_out_path)
