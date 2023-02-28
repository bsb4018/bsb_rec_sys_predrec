import os,sys
from src.logger import logging
from src.exception import PredictionException
from src.components.store_artifacts import StorageConnection
from src.configurations.mongo_config import MongoDBClient
from src.utils.main_utils import load_object,read_json_file
from src.constants.file_constants import PRODUCTION_MODEL_FILE_PATH,INTERACTIONS_MODEL_FILE_PATH,INTERACTIONS_MATRIX_SHAPE_FILE_PATH,MODEL_USERS_ID_MAP,MODEL_USERS_FEATURE_MAP,FEATURE_STORE_FILE_PATH,COURSES_DATA_FILE_PATH
from feast import FeatureStore
import pandas as pd
import json
import random
from lightfm import LightFM
from lightfm.evaluation import auc_score
import numpy as np
from scipy import sparse

class RecommendCourse:
    '''
    Getting Recommendations From Api Input
    '''
    def __init__(self):
        try:
            logging.info("Connecting Course Recommender")
            self.store_artifacts = StorageConnection()
            self.mongo_client = MongoDBClient()
            self.connection = self.mongo_client.dbcollection
            self.course_connection = self.mongo_client.course_collection
            logging.info("Course Recommender Connection Successful")
        except Exception as e:
            raise PredictionException(e,sys)


    def g(self,item_dict):
        '''
        Input:- Existing User ID [0-3999]
        Output: - Recommendation For the input User ID based on other simillar users
        '''
        try:
            logging.info("Into recommend_by_similar_user_activity method of RecommendCourse class")

            logging.info("Downloading artifacts from S3 if not already present")
            self.store_artifacts.download_production_model_s3()
            
            #load model from artifact
            logging.info("Loading Best Model Artifacts")
            timestamps = list(map(int, os.listdir(PRODUCTION_MODEL_FILE_PATH)))
            latest_timestamp = max(timestamps)
            latest_production_interaction_model = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MODEL_FILE_PATH)
            latest_production_interaction_matrix_shape_file = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MATRIX_SHAPE_FILE_PATH)
            
            #Load Model
            interaction_model = load_object(latest_production_interaction_model)
            #Load User-Id Map 
            user_id_map = load_object(os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", MODEL_USERS_ID_MAP))
            #Load Sparse Matrxix Shape
            interaction_matrix_shape = read_json_file(latest_production_interaction_matrix_shape_file)
            n_items = int(interaction_matrix_shape["n_items"])

            #Get the user from input
            user_id = item_dict["user_id"]

            #Map the user from the user-id map
            mapped_user_id = user_id_map[user_id]

            logging.info("Getting Recommendations For Existing Users Based on Simillar Interests Between Users")
            #Get Top 4 recommendations Course ID
            scores = interaction_model.predict(mapped_user_id, np.arange(n_items))
            top_items = np.argsort(-scores)
            top_4_items = top_items[0:4]
            print(top_4_items)
            cidx = top_4_items.tolist()
            print(cidx)
            for item in cidx:
                item = item+1

            #Map the Top 4 recommendations From the Course ID -> Course Name using Mongo DB
            course_data = []
            course1 = self.course_connection.find({'course_id': cidx[0]}, {'_id': 0, 'course_name':1}).next()
            course2 = self.course_connection.find({'course_id': cidx[1]}, {'_id': 0, 'course_name':1}).next()
            course3 = self.course_connection.find({'course_id': cidx[2]}, {'_id': 0, 'course_name':1}).next()
            course4 = self.course_connection.find({'course_id': cidx[3]}, {'_id': 0, 'course_name':1}).next()
            course_data.append(dict(course1).get("course_name"))
            course_data.append(dict(course2).get("course_name"))
            course_data.append(dict(course3).get("course_name"))
            course_data.append(dict(course4).get("course_name"))
            
            logging.info("Exiting recommend_by_similar_user_activity method of RecommendCourse class")
            return True,course_data
        
        except Exception as e:
            raise PredictionException(e,sys)

        
    def recommend_for_new_user(self,item_dict):
        '''
        Input:- New User ID
        Output: - Recommendation For the input User ID based User Features
        '''
        try:
            logging.info("Into recommend_for_new_user method of RecommendCourse class")
            
            logging.info("Downloading artifacts from S3 if not already present")
            self.store_artifacts.download_production_model_s3()

            #load model from artifact
            logging.info("Loading Best Model Artifacts")
            timestamps = list(map(int, os.listdir(PRODUCTION_MODEL_FILE_PATH)))
            latest_timestamp = max(timestamps)
            latest_production_interaction_model = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MODEL_FILE_PATH)
            latest_production_interaction_matrix_shape_file = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MATRIX_SHAPE_FILE_PATH)
            interaction_model = load_object(latest_production_interaction_model)

            user_feature_map = load_object(os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", MODEL_USERS_FEATURE_MAP))

            interaction_matrix_shape = read_json_file(latest_production_interaction_matrix_shape_file)
            n_items = int(interaction_matrix_shape["n_items"])


            user_feature_list = []
            for key, value in item_dict.items():
                valstr = str(value)
                keystr = str(key)
                format_feature = keystr+":"+valstr
                user_feature_list.append(str(format_feature))
            
            logging.info("Formatting user features for prediction")    
            new_user_features = self._format_newuser_input(user_feature_map, user_feature_list)

            logging.info("Getting Recommendations for New Users")
            scores = interaction_model.predict(0, np.arange(n_items), user_features=new_user_features) # Here 0 means pick the first row of the user_features sparse matrix
            
            top_items = np.argsort(-scores)

            #Get Top 4 recommendations Course ID
            top_4_items = top_items[0:4]

            cidx = top_4_items.tolist()
            print(cidx)
            for item in cidx:
                item = item+1

            #Map the Top 4 recommendations From the Course ID -> Course Name using Mongo DB
            course_data = []
            course1 = self.course_connection.find({'course_id': cidx[0]}, {'_id': 0, 'course_name':1}).next()
            course2 = self.course_connection.find({'course_id': cidx[1]}, {'_id': 0, 'course_name':1}).next()
            course3 = self.course_connection.find({'course_id': cidx[2]}, {'_id': 0, 'course_name':1}).next()
            course4 = self.course_connection.find({'course_id': cidx[3]}, {'_id': 0, 'course_name':1}).next()
            course_data.append(dict(course1).get("course_name"))
            course_data.append(dict(course2).get("course_name"))
            course_data.append(dict(course3).get("course_name"))
            course_data.append(dict(course4).get("course_name"))
            
            logging.info("Exiting recommend_for_new_user method of RecommendCourse class")
            return True,course_data
        except Exception as e:
            raise PredictionException(e,sys)
        
    def _format_newuser_input(self,user_feature_map, user_feature_list):
        '''
        Input -> Trained User Feature Map
        Output -> Formatted User Feature List
        '''
        try:
            logging.info("Enter _format_newuser_input method of RecommendCourse class")
            normalised_val = 1.0 
            target_indices = []
            for feature in user_feature_list:
                try:
                    target_indices.append(user_feature_map[feature])
                except KeyError:
                    print("new user feature encountered '{}'".format(feature))
                    pass
        
            new_user_features = np.zeros(len(user_feature_map.keys()))
            for i in target_indices:
                new_user_features[i] = normalised_val
            new_user_features = sparse.csr_matrix(new_user_features)

            logging.info("Exiting  _format_newuser_input method of RecommendCourse class")
            return (new_user_features)
        
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_interest(self,item_dict):
        '''
        Input:- Interest Tags
        Output: - Recommendation based on Interest Tags
        '''
        try:
            logging.info("Into recommend_by_similar_interest method of RecommendCourse class")
            logging.info("Getting Recommendation By Any List of Interests")

            #Gettinmg Recommendation By Searching Mongo DB Database for each tag
            courses = []
            if item_dict["web_dev"] == 1:
                tag = "web_dev"
                courses.append(self._find_courses_interest(tag))
            if item_dict["data_sc"] == 1:
                tag = "data_sc"
                courses.append(self._find_courses_interest(tag))
            if item_dict['data_an'] == 1:
                tag = "data_an"
                courses.append(self._find_courses_interest(tag))
            if item_dict['game_dev'] == 1:
                tag = "game_dev"
                courses.append(self._find_courses_interest(tag))
            if item_dict['mob_dev'] == 1:
                tag = "mob_dev"
                courses.append(self._find_courses_interest(tag))
            if item_dict['program'] == 1:
                tag = "program"
                courses.append(self._find_courses_interest(tag))
            if item_dict['cloud'] == 1:
                tag = "cloud"
                courses.append(self._find_courses_interest(tag))

            logging.info("Exiting recommend_by_similar_interest method of RecommendCourse class")
            return courses
            
        except Exception as e:
            raise PredictionException(e,sys)


    def _find_courses_interest(self,tag: str):
        '''
        Input -> Interest Topic Tag
        Output -> Courses List Similar to the Topic Tag
        '''
        try:
            logging.info("Into _find_courses_interest helper method of RecommendCourse class")

            #Getting Courses Randomly
            randomnos = random.randint(1,15)
            courses1 = self.connection.find({'category': tag}, {'_id': 0, 'course_name':1}).skip(randomnos)
            
            recommended_list = []
            recommended_list.append(dict(courses1.next()).get("course_name"))
            recommended_list.append(dict(courses1.next()).get("course_name"))
            recommended_list.append(dict(courses1.next()).get("course_name"))

            logging.info("Exiting _find_courses_interest helper method of RecommendCourse class")
            return recommended_list

        except Exception as e:
            raise PredictionException(e,sys)