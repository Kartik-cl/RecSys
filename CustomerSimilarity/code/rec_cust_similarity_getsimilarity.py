
'''
This script takes the LSH output as its input and finds cosine similarity between the pairs of customers we are interested in
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
from pyspark.sql.window import Window
from pyspark.sql.functions import rank, col
from pyspark.sql.functions import desc
import sys
from pyspark import SparkFiles
############# end of all the imports ##################


#returns cosine similarity between two customer indexes
def get_similarity(cust_dna_dict,cus_index1,cus_index2):
    vec1 = cust_dna_dict[cus_index1]
    vec2 = cust_dna_dict[cus_index2]
    similarity = cosine_similarity(vec1,vec2)[0][0]
    return similarity
            

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
red_data_path = config.get('REDUCED_DATASET', 'red_dataset_path')
neigh_info_path = sys.argv[2]#config.get('NEIGHBOURS', 'neigh_info_path')
sim_out_path = sys.argv[3]#config.get('NEIGHBOURS_SIM_SCORE', 'sim_out_path') #can be changed in the config file wherever the similarity output is desired
###########reading the configuration file and parameters###########


cust_dna = spark.read.format('parquet').load(red_data_path)
lsh_res = spark.read.format('parquet').load(neigh_info_path)
cust_dna_collected=(cust_dna
                    .rdd
                    .map(lambda x:(x['id'],np.array(x['pca_features'])))
                    ).collect()
cust_dna_dict= {t[0]:t[1:] for t in cust_dna_collected}

lsh_res_filtered = (lsh_res
        .filter('no_of_collision>1'))

# count_df=(lsh_res_filtered
#  .groupBy('cust_sim_from')
#  .count()
# # .show()
# )

# count_extra_df = (count_df
# .filter('count>500'))

# remove = (count_extra_df
# .rdd
# .map(lambda x: x[0])).collect()

# df_less_neigh = (lsh_res_filtered
# .filter(~lsh_res_filtered.cust_sim_from.isin(remove)))

# df_more_neigh = (lsh_res_filtered
# .filter(lsh_res_filtered.cust_sim_from.isin(remove)))


# df_temp = (df_more_neigh
#  .rdd
#  .map(lambda x: (x[0],x[1],float(get_similarity(cust_dna_dict,x[0],x[1]))))).toDF(['cust_sim_from','cust_sim_to','similarity'])

# window = Window.partitionBy(df_temp['cust_sim_from']).orderBy(df_temp['similarity'].desc())

# df_sim = (df_temp.select('*', rank().over(window).alias('rank')) 
#   .filter(col('rank') <= 500) 
#   .select('cust_sim_from','cust_sim_to','similarity'))

# df_sim1 = (df_less_neigh
#  .rdd
#  .map(lambda x: (x[0],x[1],float(get_similarity(cust_dna_dict,x[0],x[1]))))).toDF(['cust_sim_from','cust_sim_to','similarity'])

lsh_results = (lsh_res_filtered
.rdd
.map(lambda x: (x[0],x[1],float(get_similarity(cust_dna_dict,x[0],x[1]))))).toDF(['cust_sim_from','cust_sim_to','similarity'])


disk_storage= StorageLevel(True, False, False, False, 1)
lsh_res_filtered.persist(disk_storage)

output_rdd = (lsh_results
              .rdd
             .map(lambda x:(x[0],[x[0],'c',x[1],x[2]])))
output_rdd.saveAsTextFile(sim_out_path)


