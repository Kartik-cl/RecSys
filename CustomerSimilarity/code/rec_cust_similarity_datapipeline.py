'''
This is the first part of the getting similarity piece. This script takes in the customer DNA input, throws out the reduced customer dna after applying prinicipal components analysis(PCA)
in order to reduce the number of features such that these reduced features retain most of the variance captued by the customer dna and make the calculations feasible for the next steps
'''

############# start of all the imports ##################
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
from pyspark.sql.functions import udf, col
import sys
import pickle
from pyspark import SparkFiles
############# end of all the imports ##################



#defining the spark variable in order to get the spark SQL and sparkcontext capabilities
spark = SparkSession.builder.appName("MyApp").getOrCreate()


'''
This Datapipeline class takes in the customer DNA, selects the necessary features, does transformation(rank standardisation),
performs PCA and writes the reduced output to be used in the further steps
'''
class Datapipeline:
    #constructor declaration initial configuration
    def __init__(self,configpath):
        # self.config = cp.ConfigParser()
        # self.config.read(configpath)
        spark.sparkContext.addFile(configpath)
        self.configFile = SparkFiles.get(configpath)
        self.config = cp.RawConfigParser()
        self.config.read(self.configFile)
        self.file_to_process = self.config.get('CSV_DATAPATH', 'DATAPATH')
        self.out_path = self.config.get('REDUCED_DATASET', 'red_dataset_path')  #path of the reduced product dna, can be changed from the config file to whichever path at which the output is required
        self.num_pc=0
    
    
    #loads the dataset and returns it
    def getdataset(self):
        path = self.file_to_process
        cust_dna = spark.read.format("com.databricks.spark.csv").option("header","true").option("inferSchema", "true").load(path)
        #cust_dna = cust_dna.sample(False, 0.00406565, 100)
        return cust_dna
    
    #Returns names of relevant attributes to be selected
    def attributenames(self):
        attributes = self.config.get('ATTRIBUTES','LIST_OF_ATTRIBUTES')
        attributes = attributes.split(', ')
        return attributes
    
    #does rank standardization and returns the transformed dataset and the model used to transform it
    def transformation(self, df):

        '''
        sample example
        before the scalar transformation:
        Row(id = 1234, features = DenseVector([0.0, 20, 12 ...])
        
        After the scalar transformation
        Row(id = 1234, features = DenseVector([0.0, 0.2, 0.12 ...])
        '''
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
              .map(lambda x: (int(x[0]),Vectors.dense(x[1:])))).toDF(['id','features'])
        scaler = MinMaxScaler(inputCol="features", outputCol="scaledFeatures")
        # Compute summary statistics and generate MinMaxScalerModel
        scalerModel = scaler.fit(df)
        scaledData = scalerModel.transform(df)
        df = scaledData.select("id","scaledFeatures")
        return df, scalerModel
    
    
    #removes unwanted attributes and returns the resultant dataset
    def truncateddataset(self):
        cust_dna = self.getdataset()
        attributes = self.attributenames()
        cust_dna = cust_dna.select(attributes)
        return cust_dna
        
    
    #returns the variance the pca expects to capture
    def variancethreshold(self):
        return self.config.get('VARIANCE_CAPTURED','variance_threshold')
     
    
    #reducing dimensionality of the resultant dataset through pca    
    def pca(self,cust_dna,var,initial_num_pc):
        '''
        sample example
        The output of this function is of the following format:
        Row(id = 1234, pca_features = DenseVector([0.4494, -0.6573, 0.1983 ... ]))
        '''
        cust_dna, scalerModel = self.transformation(cust_dna)
        pca = PCA(k=initial_num_pc, inputCol="scaledFeatures", outputCol="pca_features")
        pca_model = pca.fit(cust_dna)
        var_sum = np.cumsum(np.sort(pca_model.explainedVariance)[::-1]) # Return
        self.num_pc = np.argwhere(np.cumsum(pca_model.explainedVariance)<var)[-1][0]+2 # Return
        eigen_vecs = pca_model.pc.toArray()[:,:self.num_pc] # Return      
        pca = PCA(k=self.num_pc, inputCol="scaledFeatures", outputCol="pca_features")
        pca_model = pca.fit(cust_dna)
        features = pca_model.transform(cust_dna)
        reduced_cust_dna = features.select('id','pca_features') 
        return [self.num_pc, reduced_cust_dna, pca_model, scalerModel]
    
    
    #writes the PCA output to the desired location
    def write_out(self, red_cust_dna):
        out_path = self.out_path
        red_cust_dna.write.save(out_path, mode = 'overwrite')
        
    #save the PCA and scaler models to the desired location
    def save_models(self, pca_model, scaler_model):
        pca_model_path = self.config.get('MODEL_PATHS','pca_model') # path to the pca model. can be changed wherever desired in the config file
        scaler_model_path = self.config.get('MODEL_PATHS','scaler_model') # path to the scaler model. can be changed wherever desired in the config file
        pca_model.write().overwrite().save(pca_model_path)
        scaler_model.write().overwrite().save(scaler_model_path)
        
    



configpath_datapipeline =  sys.argv[1] #'/data/usr/RecommendationEngine/batch/CustomerSimilarity/config/config_indexed.ini' # reading the configuration file
dataPipeline = Datapipeline(configpath_datapipeline) # creating an instance of the Datapipeline class
cust_dna = dataPipeline.truncateddataset() # getting the dataset with necessary fields
#cust_dna = cust_dna.sample(False, 0.05, 100)


initial_num_pc = int(len(cust_dna.columns)*float(dataPipeline.variancethreshold())) #initial no. of principal components
pca_results = dataPipeline.pca(cust_dna, float(dataPipeline.variancethreshold()), initial_num_pc) #getting the pca results
num_dims,red_cust_dna, pca_model, scaler_model = pca_results
dataPipeline.save_models(pca_model,scaler_model) #saving the PCA and Scaler models
dataPipeline.write_out(red_cust_dna) #Writing out the PCA results

