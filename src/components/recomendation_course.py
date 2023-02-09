import os,sys
from src.logger import logging
from src.exception import PredictionException
from src.components.store_artifacts import StorageConnection
from src.configurations.mongo_config import MongoDBClient
from src.utils.main_utils import load_object,read_json_file
from src.constants.file_constants import PRODUCTION_MODEL_FILE_PATH,INTERACTIONS_MODEL_FILE_PATH,INTERACTIONS_MATRIX_SHAPE_FILE_PATH,FEATURE_STORE_FILE_PATH,COURSES_DATA_FILE_PATH
from feast import FeatureStore
import pandas as pd
import json
import random
from lightfm import LightFM
from lightfm.evaluation import auc_score
import numpy as np


class RecommendCourse:
    def __init__(self):
        try:
            self.store_artifacts = StorageConnection()
            self.mongo_client = MongoDBClient()
            self.connection = self.mongo_client.dbcollection
            self.course_connection = self.mongo_client.course_collection
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_user_activity(self,item_dict):
        try:
            #load model from artifact
            self.store_artifacts.download_production_model_s3()
            timestamps = list(map(int, os.listdir(PRODUCTION_MODEL_FILE_PATH)))
            latest_timestamp = max(timestamps)
            latest_production_interaction_model = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MODEL_FILE_PATH)
            latest_production_interaction_matrix_shape_file = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MATRIX_SHAPE_FILE_PATH)
            interaction_model = load_object(latest_production_interaction_model)

            interaction_matrix_shape = read_json_file(latest_production_interaction_matrix_shape_file)
            n_items = int(interaction_matrix_shape["n_items"])

            #get the user from input
            user_id = item_dict["user_id"]

            #get recommendation
            scores = interaction_model.predict(user_id, np.arange(n_items))
            top_items = np.argsort(-scores)
            top_4_items = top_items[0:4]
            print(top_4_items)
            cidx = top_4_items.tolist()
            print(cidx)
            for item in cidx:
                item = item+1

            
            course_data = []
            course1 = self.course_connection.find({'course_id': cidx[0]}, {'_id': 0, 'course_name':1}).next()
            course2 = self.course_connection.find({'course_id': cidx[1]}, {'_id': 0, 'course_name':1}).next()
            course3 = self.course_connection.find({'course_id': cidx[2]}, {'_id': 0, 'course_name':1}).next()
            course4 = self.course_connection.find({'course_id': cidx[3]}, {'_id': 0, 'course_name':1}).next()
            course_data.append(dict(course1).get("course_name"))
            course_data.append(dict(course2).get("course_name"))
            course_data.append(dict(course3).get("course_name"))
            course_data.append(dict(course4).get("course_name"))
            

            '''
            store = FeatureStore(repo_path="feature_repo")
            course_data = store.get_online_features(features = ["course_features:course_id","course_features:course_name"],\
                                                    entity_rows=[{"course_feature_id": cidx[0]},{"course_feature_id": cidx[1]},\
                                                                 {"course_feature_id": cidx[2]},{"course_feature_id": cidx[3]}]\
                                                                    ).to_dict().get("course_name")
            print(course_data)
            #coursesdf = pd.DataFrame(course_data)
            #print(coursesdf.head())
            '''

            #c=0
            #recmd_courses_list = []
            #for id in cidx:
            #    if c == 4:
            #        break
            #    c += 1
            #    recmnd_course = coursesdf[coursesdf["course_id"] == id]["course_name"].values
            #    recmd_courses_list.append(recmnd_course)


            #new_recommend_list = []
            #for course in recmd_courses_list:
            #    for value in course:
            #        new_recommend_list.append(value)

            #recomendations_format = {}

            #use recommend function of the model to get the recommendation
            #if not recmd_courses_list:
            #    recomendations_format = dict({"Recommendations": "No Recommendations Available"})
            #    recommendation_response = json.dumps(recomendations_format)
            #    return False,recommendation_response
            #else:
                #recomendations_format = dict({"Recommendation 1" : new_recommend_list[0],
                #    "Recommendation 2" : new_recommend_list[1],"Recommendation 3" : new_recommend_list[2],
                #        "Recommendation 4" : new_recommend_list[3]})
                #recommendation_response = json.dumps(recomendations_format)
            #    return True,new_recommend_list              #recommendation_response
            return True,course_data
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_interest(self,item_dict):
        try:
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

            return courses
            
        except Exception as e:
            raise PredictionException(e,sys)

    def _find_courses_interest(self,tag: str):
        try:
            randomnos = random.randint(1,15)
            courses1 = self.connection.find({'category': tag}, {'_id': 0, 'course_name':1}).skip(randomnos)
            
            recommended_list = []
            recommended_list.append(dict(courses1.next()).get("course_name"))
            recommended_list.append(dict(courses1.next()).get("course_name"))
            recommended_list.append(dict(courses1.next()).get("course_name"))

            return recommended_list

        except Exception as e:
            raise PredictionException(e,sys)