from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Union, Any
import uvicorn
from fastapi import FastAPI, File, UploadFile
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from src.components.recomendation_course import RecommendCourse
from pydantic import BaseModel
from src.constants.app_constants import APP_HOST,APP_PORT

app = FastAPI(title="RecommenderPrediction-Server")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


class Interest_Item(BaseModel):
    web_dev: int
    data_sc: int
    data_an: int
    game_dev: int
    mob_dev: int
    program: int
    cloud: int

class Course_Name(BaseModel):
    course_name: str

class User_Id(BaseModel):
    user_id: int

@app.post("/recommendations_by_interest")
def get_recommendations_by_interest(item: Interest_Item):
    try:
        
        item_dict = item.dict()
        recommend_course = RecommendCourse()
        status = recommend_course.recommend_by_similar_interest(item_dict)
        if status == True:
            return {"User_Course Interaction Added Successfully"}
        else:
            return {"Invalid Data Entered"}
        
    except Exception as e:
        raise Response(f"Error Occured! {e}")


@app.post("/recommendations_by_course")
def get_recommendations_by_similar_courses(item: Course_Name):
    try:
        
        item_dict = item.dict()
        recommend_course = RecommendCourse()
        status = recommend_course.recommend_by_similar_course(item_dict)
        if status == True:
            return {"Course Data Added Successfully"}
        else:
            return {"Invalid Data Entered"}
        
    except Exception as e:
        raise Response(f"Error Occured! {e}")


@app.post("/recommendations_by_user")
def recommendations_by_similar_user_activity(item: User_Id):
    try:
        item_dict = item.dict()
        recommend_course = RecommendCourse()
        status = recommend_course.recommend_by_similar_user_activity(item_dict)
        if status == True:
            return {"Course Data Added Successfully"}
        else:
            return {"Invalid Data Entered"}
        
    except Exception as e:
        raise Response(f"Error Occured! {e}")


if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)