##### importing packages #####
from pyspark.sql import SparkSession 
from pyspark.sql import *
import pyspark.sql.functions as sf
from pyspark.sql.functions import col
from pyspark.sql.functions import udf
##### end of imports #####

##### ********* CONFIGURATION FILE AND SPARK SESSION INITIATION *********#####
##### ********* *********************************************************#####


spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

config = cp.ConfigParser()
config.read('../config/config.ini')



in_file_path = config.get('FILEPATH','INPUT_FILE_PATH_INCR')

in_threshold_val2   = float(config.get('PARAM_THRESHOLD','LEVEL2_CHNL_DSPCTGR_CD_TH'))
in_threshold_val3   = float(config.get('PARAM_THRESHOLD','LEVEL3_CHNL_DSPCTGR_CD_TH'))

def jaccard_sim(p,q):
    return float(len(set(p) & set(q)))/len(set(p) | set(q))

def jaccard_dict(p_l3, p_attr,q_l3, q_attr):
    print("jaccard dict called")
    p_lvl3 = p_l3
    q_lvl3 = q_l3
    p_new = p_attr.asDict()
    q_new = q_attr.asDict()
    print(type(p_new))
    p1 = p_new.keys()
    q1 = q_new.keys()
    pq_intersect = set(p1) & set(q1)
    #deno = len(pq_intersect)
    deno = 0
    nume = 0.0
    for i in pq_intersect:
        if type(p_new[i]) is not list:
            p_new[i]=[p_new[i]]
        if type(q_new[i]) is not list:
            q_new[i]=[q_new[i]]
        if p_new[i] == [None] and q_new[i] == [None]:
            continue
        nume = nume + jaccard_sim(p_new[i],q_new[i])
        deno = deno +1
    if deno == 0:
        final_jaccard = 0
    else:
        final_jaccard = nume/deno
    if p_lvl3 == q_lvl3:
        in_threshold_val = in_threshold_val3
    else:
        in_threshold_val = in_threshold_val2
    return max(in_threshold_val,final_jaccard)


prod_dna_incr = spark.read.json(in_file_path)

dfx = prod_dna_incr.select('display_category_l2_cd','product_index','display_category_l3_cd','attributes')

df  = dfx.withColumnRenamed('display_category_l2_cd','LEVEL2_p1').withColumnRenamed('product_index','p1').withColumnRenamed('display_category_l3_cd','LEVEL3_p1').withColumnRenamed('attributes','attr1')
df1  = dfx.withColumnRenamed('display_category_l2_cd','LEVEL2_p2').withColumnRenamed('product_index','p2').withColumnRenamed('display_category_l3_cd','LEVEL3_p2').withColumnRenamed('attributes','attr2')

df_new = df.join(df1, df.LEVEL2_p1 == df1.LEVEL2_p2)
dfz = df_new.filter(df_new.p1 >= df_new.p2)

dfx_old = prod_dna.select('display_category_l2_cd','product_index','display_category_l3_cd','attributes')
df_old  = dfx_old.withColumnRenamed('display_category_l2_cd','LEVEL2_p1').withColumnRenamed('product_index','p1').withColumnRenamed('display_category_l3_cd','LEVEL3_p1').withColumnRenamed('attributes','attr1')
df_on = df_old.join(df1, df_old.LEVEL2_p1 == df1.LEVEL2_p2)
dfz_new = df_on.union(dfz)

udf_dict = udf(jaccard_dict)
new_df = dfz_new.withColumn('score', udf_dict(dfz_new.LEVEL3_p1,dfz_new.attr1, dfz_new.LEVEL3_p2, dfz_new.attr2 ))

jsm = new_df.select('p1','p2','score')
rddhb=jsm.rdd.map(lambda x : (str(x[0]), [str(x[0]), 'p' , str(x[1]), str(x[2])]))

##### output the write results #####

##### placeholder for write #####

##### output the write results #####