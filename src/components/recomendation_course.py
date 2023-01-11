import os,sys
from src.logger import logging
from src.exception import PredictionException
from src.components.store_artifacts import StorageConnection
from src.utils.main_utils import load_object
from src.constants.file_constants import PRODUCTION_MODEL_FILE_PATH,INTERACTIONS_MODEL_FILE_PATH,COURSES_MODEL_FILE_PATH,INTERACTIONS_MATRIX_FILE_PATH,FEATURE_STORE_FILE_PATH
from feast import FeatureStore
import pandas as pd
import json

class RecommendCourse:
    def __init__(self):
        try:
            self.store_artifacts = StorageConnection()
        except Exception as e:
            raise PredictionException(e,sys)

    def recommend_by_similar_course(self,item_dict):
        try:
            #load model from artifact from s3
           
            #use recommend function of the model to get the recommendation
            pass
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_user_activity(self,item_dict):
        try:
            #load model from artifact
            self.store_artifacts.download_production_model_s3()
            timestamps = list(map(int, os.listdir(PRODUCTION_MODEL_FILE_PATH)))
            latest_timestamp = max(timestamps)
            latest_production_interaction_model = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MODEL_FILE_PATH)
            latest_production_interaction_matrix = os.path.join(PRODUCTION_MODEL_FILE_PATH, f"{latest_timestamp}", INTERACTIONS_MATRIX_FILE_PATH)
            interaction_model = load_object(latest_production_interaction_model)
            interaction_matrix = load_object(latest_production_interaction_matrix)

            #get the user from input
            user_id = item_dict["user_id"]

            #get recommendation 
            ids, scores = interaction_model.recommend(user_id, interaction_matrix[user_id], N=5, filter_already_liked_items=False)
            cidx = ids.tolist()

            self.store = FeatureStore(repo_path=FEATURE_STORE_FILE_PATH)
            course_data = self.store.get_online_features(features = \
            ["courses_df_feature_view:course_id",\
                "courses_df_feature_view:course_name"],
                    entity_rows=[
                        {"course_feature_id": cidx[0]},
                        {"course_feature_id": cidx[1]},
                        {"course_feature_id": cidx[2]},
                        {"course_feature_id": cidx[3]},
                        {"course_feature_id": cidx[4]}
                    ]).to_dict()

            coursesdf = pd.DataFrame(course_data)

            c=0
            recmd_courses_list = []
            for id in cidx:
                if c == 5:
                    break
                c += 1
                recmnd_course = coursesdf[coursesdf["course_id"] == id]["course_name"].values
                recmd_courses_list.append(recmnd_course)


            new_recommend_list = []
            for course in recmd_courses_list:
                for value in course:
                    new_recommend_list.append(value)

            recomendations_format = {}

            #use recommend function of the model to get the recommendation
            if not recmd_courses_list:
                recomendations_format = dict({"Recommendations": "No Recommendations Available"})
                recommendation_response = json.dumps(recomendations_format)
                return False,recommendation_response
            else:
                recomendations_format = dict({"Recommendation 1" : new_recommend_list[0],\
                    "Recommendation 2" : new_recommend_list[1],"Recommendation 3" : new_recommend_list[2],\
                        "Recommendation 4" : new_recommend_list[3],"Recommendation 5" : new_recommend_list[4]})
                recommendation_response = json.dumps(recomendations_format)
                return True,recommendation_response
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_interest(self,item_dict):
        try:
            #load model from artifact
            
            #use recommend function of the model to get the recommendation
            pass
        except Exception as e:
            raise PredictionException(e,sys)