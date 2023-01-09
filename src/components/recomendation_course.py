import sys
from src.logger import logging
from src.exception import PredictionException



class RecommendCourse:
    def __init__(self,):
        try:
            pass
        except Exception as e:
            raise PredictionException(e,sys)

    def recommend_by_similar_course(item_dict):
        try:
            #load model from artifact
            
            #use recommend function of the model to get the recommendation
            pass
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_user_activity(item_dict):
        try:
            #load model from artifact
            
            #use recommend function of the model to get the recommendation
            pass
        except Exception as e:
            raise PredictionException(e,sys)


    def recommend_by_similar_interest(item_dict):
        try:
            #load model from artifact
            
            #use recommend function of the model to get the recommendation
            pass
        except Exception as e:
            raise PredictionException(e,sys)