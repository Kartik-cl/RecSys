from pyspark.ml.clustering import KMeansModel
from pyspark.ml.feature import MinMaxScalerModel
from pyspark.ml.feature import PCAModel
import configparser as cp
from pyspark.sql import SparkSession 
import configparser as cp
import numpy as np
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import PCA
from pyspark.mllib.linalg import *
from pyspark.ml.linalg import Vectors, VectorUDT,SparseVector
from numpy.linalg import eigh
from pyspark.sql import Row
from pyspark.ml.clustering import KMeans, KMeansModel
from pyspark.ml.feature import VectorAssembler
from numpy import array
from math import sqrt
from collections import defaultdict
from scipy import sparse
from pyspark.sql.functions import *
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType

spark = SparkSession.builder.appName("MyApp").getOrCreate()

configpath = '/data/usr/RecommendationEngine/batch/CustomerSimilarity/config/config_indexed.ini'
config = cp.ConfigParser()
config.read(configpath)

class Datapipeline:
    #constructor declaration initial configuration
    def __init__(self,configpath):
        self.config = cp.ConfigParser()
        self.config.read(configpath)
        self.pca_model_path = self.config.get('MODEL_PATHS','pca_model')
        self.scaler_model_path = self.config.get('MODEL_PATHS','scaler_model')
        self.pca_model = PCAModel.load(self.pca_model_path)
        self.scaler_model = MinMaxScalerModel.load(self.scaler_model_path)
    #returns the location of the dataset
    def getdatapath(self):
        return self.config.get('CSV_DATAPATH','DATAPATH_INCR')
    #loads the dataset and returns it
    def getdataset(self):
        path = self.getdatapath()
        print (path)
        cust_dna = spark.read.format("com.databricks.spark.csv")\
         .option("header","true")\
         .option("inferSchema", "true")\
         .load(path)
        return cust_dna
    #Returns relevant attributes to be selected
    def attributenames(self):
        attributes = self.config.get('ATTRIBUTES','LIST_OF_ATTRIBUTES')
        attributes = attributes.split(', ')
        return attributes
    #For further transformations of the dataset, yet to be decided
    def transformation(self, df): #doing rank standardisation
        x = [-1] * len(df.columns)
        x = tuple(x)
        x = [x]
        row_to_add = spark.createDataFrame(x)
        cols = [i.name for i in df.schema.fields if(str(i.dataType) == "StringType")]
        df = df.union(row_to_add)
        for name in cols:
            df = df.withColumn(name, df[name].cast("float"))
        df = df.fillna(0)
        df = (df.rdd
              .map(lambda x: (x[0],Vectors.dense(x[1:])))).toDF(['id','features'])
        scaledData = self.scaler_model.transform(df)
        df = scaledData.select("id","scaledFeatures")
        return df
    #Removes unwanted attributes
    def truncateddataset(self):
        cust_dna = self.getdataset()
    # ordered_list = []
    # ordered_list.append('CustomerIndex')
    # for i in cust_dna.columns:
    #     if i!='CustomerIndex':
    #         ordered_list.append(i)
    # cust_dna = cust_dna.select(ordered_list)
    # count_df = cust_dna.agg(*[F.count(c).alias(c) for c in cust_dna.columns]).toPandas()
    # count_df = count_df.loc[:, (count_df != 0).any(axis=0)]
    # relevant_attributes = list(count_df)
        attributes = self.attributenames()
    # set_2 = set(attributes)
    # intersection = [x for x in relevant_attributes if x in set_2]
    #attributes = list(set(relevant_attributes).intersection(attributes))
        cust_dna = cust_dna.select(attributes)
        return cust_dna
    #Returns the variance the pca expects to capture
    def variancethreshold(self):
        return self.config.get('VARIANCE_CAPTURED','variance_threshold')  
    #Reducing dimensionality of the resultant dataset through pca    
    def pca(self,cust_dna,var,initial_num_pc):
        cust_dna = self.transformation(cust_dna)
        features = self.pca_model.transform(cust_dna)
        print (features.columns)
        reduced_cust_dna = features.select('id', 'pca_features') 
        return reduced_cust_dna
    def write_out(self, red_cust_dna):         
        out_path = self.config.get('REDUCED_DATASET','red_dataset_path_daily_data')
        red_cust_dna.write.save(out_path, mode = 'overwrite')
    
    
#DataPipeline class
dataPipeline = Datapipeline(configpath)
cust_dna = dataPipeline.truncateddataset()
initial_num_pc = int(len(cust_dna.columns)*float(dataPipeline.variancethreshold()))#initial no. of pri
pca_results = dataPipeline.pca(cust_dna, float(dataPipeline.variancethreshold()), initial_num_pc)
red_cust_dna = pca_results
dataPipeline.write_out(red_cust_dna)
