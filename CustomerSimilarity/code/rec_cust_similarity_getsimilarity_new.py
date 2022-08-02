# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 11:46:06 2018

@author: ibm_admin
"""
import sys
import ConfigParser as cp
from pyspark import SparkFiles
from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from sklearn.metrics.pairwise import cosine_similarity

spark = SparkSession.builder.appName("MyApp").getOrCreate()

configpath = sys.argv[1]
spark.sparkContext.addFile(configpath)
configFile = SparkFiles.get(configpath)
config = cp.RawConfigParser()
config.read(configFile)

red_data_path = config.get('REDUCED_DATASET', 'red_dataset_path')
neigh_info_path = sys.argv[2]
sim_out_path = sys.argv[3]

red_cust_dna = spark.read.format('parquet').load(red_data_path)
lsh_res = spark.read.format('parquet').load(neigh_info_path)

def get_similarity(vector1, vector2):
  similarity = cosine_similarity(vector1, vector2)[0][0]
  return similarity

#Performing join operation
df1 = lsh_res.join(red_cust_dna, lsh_res.cust_sim_from == red_cust_dna.id).select(col('cust_sim_from').alias('customer'), col('cust_sim_to').alias('neighbouring_customer'), col('pca_features').alias('cust_pcaFeatures'), col('no_of_collision'))

df2 = df1.join(red_cust_dna, df1.neighbouring_customer == red_cust_dna.id).select(df1.customer, df1.neighbouring_customer, df1.cust_pcaFeatures, col('pca_features').alias('neigh_cust_pcaFeatures'), df1.no_of_collision)

lsh_res_filtered = df2.filter((col('customer') != col('neighbouring_customer')) & (col('no_of_collision') > 1)).drop('no_of_collision')

similarity_results = (lsh_res_filtered.rdd.map(lambda x : (x[0], x[1], float(get_similarity(x[2], x[3]))))).toDF(['customer', 'neighbouring_customer', 'similarity_score'])

disk_storage = StorageLevel(True, False, False, False, 1)
lsh_res_filtered.persist(disk_storage)

output_rdd = (similarity_results.rdd.map(lambda x : (x[0], [x[0], 'c', x[1], x[2]])))
output_rdd.saveAsTextFile(sim_out_path)