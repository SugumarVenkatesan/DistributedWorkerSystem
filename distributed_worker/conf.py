import glob
import os

APPLICATION_NAME = "DISTRIBUTED WORKER SYSTEM"
# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)

REDIS_HOST = "redis"
SPARK_APP_NAME = "DistributedWorkerSystem"

DATASET_INPUT_MODE = "file" #dir for directories

#for DATASET_INPUT_MODE = dir mode else None
DATASET_FILE_DIR = None#os.path.join(BASE_DIR, 'kaggle_dataset')

#for DATASET_INPUT_MODE = file mode else ()
#list of files
DATASET_FILE_LIST = (os.path.join(BASE_DIR, 'kaggle_dataset',"7210_1.csv"),
                 os.path.join(BASE_DIR, 'kaggle_dataset',"Datafiniti_Womens_Shoes.csv"),
                 os.path.join(BASE_DIR, 'kaggle_dataset',"Datafiniti_Womens_Shoes_Jun19.csv"))

DATAFRAME_FILTER_COLUMNS = ["id","dateAdded","brand","colors"]
