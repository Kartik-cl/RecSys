'''
This script takes in the similarity results and stores it in an Hbase table
'''
#############start of all the imports ##################
from pyspark import SparkConf, SparkContext
import configparser as cp
import sys
from pyspark import SparkFiles
from pyspark.sql import SparkSession
############# end of all the imports ##################

###########reading the configuration file and parameters###########

#defining the spark variable in order to get the spark SQL and sparkcontext capabilities
spark = SparkSession.builder.appName("MyApp").getOrCreate() 

config_file_path= sys.argv[1]
# config = cp.ConfigParser()
# config.read(config_file_path)
spark.sparkContext.addFile(config_file_path)
configFile = SparkFiles.get(config_file_path)
config = cp.RawConfigParser()
config.read(configFile)
app_name              = config.get('APP_DETAILS', 'APP_NAME')
hbase_host            = config.get('SERVER_DETAILS','HBASE_HOST')
hbase_port            = config.get('SERVER_DETAILS','HBASE_PORT')
prd_sim_tbl           = config.get('SERVER_DETAILS', 'CUSTOMER_SIMILARITY_TABLE') 
load_hbase_path       = sys.argv[2]#config.get('NEIGHBOURS_SIM_SCORE', 'sim_out_path')
###########reading the configuration file and parameters###########

rdd0=spark.sparkContext.textFile(load_hbase_path)
rdd1=rdd0.map(lambda x : x.split(", ["))
rdd2=rdd1.map(lambda x: (x[0].replace("(","") , x[1].replace(" ","").replace("])","").replace("'","").split(",")))

conf = {"hbase.zookeeper.quorum": hbase_host,
        "hbase.mapred.outputtable": prd_sim_tbl,
        "hbase.zookeeper.property.clientPort":hbase_port,
        "mapreduce.outputformat.class": "org.apache.hadoop.hbase.mapreduce.TableOutputFormat",
        "mapreduce.job.output.key.class": "org.apache.hadoop.hbase.io.ImmutableBytesWritable",
        "mapreduce.job.output.value.class": "org.apache.hadoop.io.Writable"}
keyConv = "org.apache.spark.examples.pythonconverters.StringToImmutableBytesWritableConverter"
valueConv = "org.apache.spark.examples.pythonconverters.StringListToPutConverter"

rdd2.saveAsNewAPIHadoopDataset(
    conf=conf,
    keyConverter="org.apache.spark.examples.pythonconverters.StringToImmutableBytesWritableConverter",
    valueConverter="org.apache.spark.examples.pythonconverters.StringListToPutConverter")