##### importing packages #####
from pyspark.sql import SparkSession 
from pyspark.sql import *
import pyspark.sql.functions as sf
from pyspark.sql.functions import col
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

in_file_path        = config.get('FILEPATH','INPUT_FILE_PATH')
out_file_path       = config.get('FILEPATH','OUTPUT_FILE_PATH')


in_threshold_val2   = float(config.get('PARAM_THRESHOLD','LEVEL2_CHNL_DSPCTGR_CD_TH'))
in_threshold_val3   = float(config.get('PARAM_THRESHOLD','LEVEL3_CHNL_DSPCTGR_CD_TH'))

prod_dna = spark.read.json(in_file_path)

rd = prod_dna.rdd

rdd0 =rd.map(lambda x: (x['display_category_l2_cd'],[x['product_index'],x['display_category_l3_cd'],x['attributes']])).persist()

rdd1=rdd0.join(rdd0)

rdd2=rdd1.filter(lambda x: x[1][0][0] >= x[1][1][0])

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

rdd3 = rdd2.map(lambda x : (  str(x[1][0][0]) , [str(x[1][0][0]), 'p', str(x[1][1][0]), str(jaccard_dict(x[1][0][1],x[1][0][2], x[1][1][1],x[1][1][2]))]))


##### output the write results #####

##### placeholder for write #####

##### output the write results #####