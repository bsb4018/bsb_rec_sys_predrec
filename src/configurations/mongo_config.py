import os
import sys
import certifi
import pymongo
import os,sys
from src.logger import logging
from src.constants.cloud_constants import MONGO_DATABASE_NAME,MONGO_COLLECTION_NAME,MONGODB_URL_KEY,MONGO_COURSE_COLLECTION_NAME
from src.exception import PredictionException

ca = certifi.where() #Reference the installed certificate authority(CA) bundle


class MongoDBClient:
    client = None

    def __init__(self):
        try:
            logging.info("Connecting Mongo DB")
            self.database_name = MONGO_DATABASE_NAME
            self.collection_name = MONGO_COLLECTION_NAME
            self.course_collection_name = MONGO_COURSE_COLLECTION_NAME
            if MongoDBClient.client is None:
                mongo_db_url = os.getenv(MONGODB_URL_KEY)
                if mongo_db_url is None:
                    raise Exception(f"Environment key: {MONGODB_URL_KEY} is not set")
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile = ca)
            self.client = MongoDBClient.client
            self.database = self.client[self.database_name]
            self.dbcollection = self.client[self.database_name][self.collection_name]
            self.course_collection = self.client[self.database_name][self.course_collection_name]

            logging.info("Mongo DB Connection Successful")
        except Exception as e:
            raise PredictionException(e,sys)