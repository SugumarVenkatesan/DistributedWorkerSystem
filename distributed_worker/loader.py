#!/usr/bin/python
# -*- coding: utf-8 -*--

import sys,os
sys.path.append(os.getcwd())

import os
import redis
import pyspark
import time
import multiprocessing

from datetime import datetime
from glob import glob
from pyspark.sql import SparkSession as ss
from functools import partial

from distributed_worker.conf import (REDIS_HOST,DATAFRAME_FILTER_COLUMNS,SPARK_APP_NAME,
                   DATASET_FILE_LIST,DATASET_FILE_DIR,DATASET_INPUT_MODE)

redis_conn = redis.StrictRedis(host=REDIS_HOST,decode_responses=True)
redis_pipe = redis_conn.pipeline()

######################
# SparkSession class #
######################
class SparkSession:

    # - Notes:
    # The main object if Spark Context ('sc' object).
    # All new Spark sessions ('spark' objects) are sharing the same underlying Spark context ('sc' object) into the same JVM,
    # but for each Spark context the temporary tables and registered functions are isolated.
    # You can't create a new Spark Context into another JVM by using 'sc = SparkContext(conf)',
    # but it's possible to create several Spark Contexts into the same JVM by specifying 'spark.driver.allowMultipleContexts' to true (not recommended).

    spark = None   # The Spark Session
    sc = None      # The Spark Context
    scConf = None  # The Spark Context conf
    
    def __init__(self,appname,config={}):
        self.appname = appname
        if any([isinstance(config,dict),config]):
            self.config_items = config.items()
        else:
            raise Exception("Config should be passed as dictionary like {'config_key':'config_value'}")

    def _init(self):
        self.sc = self.spark.sparkContext
        self.scConf = self.sc.getConf() # or self.scConf = self.spark.sparkContext._conf

    # Return the current Spark Session (singleton), otherwise create a new one�
    def getOrCreateSparkSession(self):
        cmd = "ss.builder"
        if (self.appname): cmd += ".appName(" + "'" + self.appname + "'" + ")"
        if (self.config_items):
            cmd += "".join([".config(" + "'" + str(key) + "'" + "," + "'" + str(value) + "'" +")" for key,value in self.config_items]+[""])
        cmd += ".getOrCreate()"
        self.spark = eval(cmd)
        self._init()
        return self.spark

    # Return the current Spark Context (singleton), otherwise create a new one via getOrCreateSparkSession()
    def getOrCreateSparkContext(self):
        self.getOrCreateSparkSession(self.appName, self.config)
        return self.sc

    # Create a new Spark session from the current Spark session (with isolated SQL configurations).
    # The new Spark session is sharing the underlying SparkContext and cached data,
    # but the temporary tables and registered functions are isolated.
    def createNewSparkSession(self, currentSparkSession):
        self.spark = currentSparkSession.newSession()
        self._init()
        return self.spark

    def getSparkSession(self):
        return self.spark

    def getSparkSessionConf(self):
        return self.spark.conf

    def getSparkContext(self):
        return self.sc

    def getSparkContextConf(self):
        return self.scConf

    def getSparkContextConfAll(self):
        return self.scConf.getAll()

    def setSparkContextConfAll(self, properties):
        # Properties example: { 'spark.executor.memory' : '4g', 'spark.app.name' : 'Spark Updated Conf', 'spark.executor.cores': '4',  'spark.cores.max': '4'}
        self.scConf = self.scConf.setAll(properties) # or self.scConf = self.spark.sparkContext._conf.setAll()

    # Stop the underlying SparkContext.
    def stopSparkContext(self):
        self.spark.stop()
        self.sc.stop()
        
    def read_csv(self,csv_filepath,header=True,sep=","):
        return self.spark.read.csv(csv_filepath, header=header, sep=sep)
        
    def __enter__(self):
        self.getOrCreateSparkSession()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stopSparkContext()

def initialize_spark_redis_csv_loader(appname,csv_file):
    with SparkSession(appname=appname,config={"source_file":csv_file.rsplit(os.sep,1)[1]}) as spark_session_obj:
        dataframe = spark_session_obj.read_csv(csv_file).cache()
        dataframe_with_required_columns = dataframe.select(DATAFRAME_FILTER_COLUMNS)
        dataframe_without_null_column_values = dataframe_with_required_columns.na.drop()
        dataframe_without_duplicate_rows = dataframe_without_null_column_values.drop_duplicates()
        final_dataframe = dataframe_without_duplicate_rows.collect()
        for each_record in final_dataframe:
            shoe_product_id,shoe_brand,shoe_colors,shoe_date_of_addition= each_record["id"],each_record["brand"],each_record["colors"],each_record["dateAdded"]
            redis_conn.hset(shoe_product_id, 'id', shoe_product_id)
            redis_conn.hset(shoe_product_id, 'shoe_brand', shoe_brand)
            redis_conn.hset(shoe_product_id, 'colors', shoe_colors)
            redis_conn.hset(shoe_product_id, 'date_of_addition', shoe_date_of_addition)
            timestamp = datetime.strptime(shoe_date_of_addition, '%Y-%m-%dT%H:%M:%SZ')
            epoch_timestamp = time.mktime(timestamp.timetuple())
            redis_conn.zadd('product_timestamp', {shoe_product_id: int(epoch_timestamp)})
            [redis_conn.zadd(shoe_color.lower(),{shoe_product_id: int(epoch_timestamp)}) for shoe_color in shoe_colors.split(',')]



class ParallelCSVSparkRedisLoader():
    def __init__(self):
        self.appname = SPARK_APP_NAME
        self.csv_file_list = DATASET_FILE_LIST if DATASET_INPUT_MODE=="file" \
                            else [fl for fl in glob(os.path.join(DATASET_FILE_DIR, 'kaggle_dataset',"*.csv"))]
        self.config = {"DATASET_FILES":",".join([each_fl.rsplit(os.sep,1)[1] for each_fl in self.csv_file_list])}
 
    def load_csv(self,pool):
        partial_func =partial(initialize_spark_redis_csv_loader,self.appname)             
        return pool.map_async(partial_func, self.csv_file_list)
 

def load():
    process_len = len(DATASET_FILE_LIST) if DATASET_INPUT_MODE=="file" \
                            else len([fl for fl in glob(os.path.join(DATASET_FILE_DIR, 'kaggle_dataset',"*.csv"))])
    pool = multiprocessing.Pool(process_len)
    r = ParallelCSVSparkRedisLoader().load_csv(pool)
    r.get()
    pool.close()
    pool.join()