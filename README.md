# Course Recommender System - Model Prediction and Serving
### Problem Statement
Course Recommender System for recommending courses to users in a education-website platform
Users Get Recommended in three ways
1. By Interest Tag -> Users enters interest topic tags and get recommendations based on that
2. By Similar Users -> Existing Users enter user id and get recommendations based on similar interactions of other users with the platform 
3. By User's Previous Experiences -> New Users who have not interacted with the platform get recommendations based on past experiences during onboarding

### Solution Proposed 
For 1. We have Stored Courses Tagwise so we take input interest topic from API and do a Mongo DB Seacrh to recommend courses.
For 2. We have trained a hybrid recommender System on user-course interaction features using LightFM framework, so we download the model and artifacts and take input the existing User ID and recommend courses based on the users with similar interactions.
For 3. We have trained a hybrid recommender System on user features using LightFM framework, so we download the model and artifacts and take input the a new User ID and user features and recommend courses based on the user features.

## Tech Stack Used
1. Python
3. AWS
4. Docker
5. MongoDB


## Infrastructure Required.
1. AWS S3
2. Git Actions
3. AWS ECR
4. AWS EC2


## How to run?
Before we run the project, make sure that you are having MongoDB in your local system, with Compass since we are using MongoDB for some data storage. You also need AWS account to access S3 Services.


## Project Architecture
![image](https://github.com/bsb4018/bsb_rec_sys_predrec/blob/main/images/model_serving.drawio.png)


### Step 1: Clone the repository
```bash
git clone https://github.com/bsb4018/bsb_rec_sys_predrec.git
```

### Step 2- Create a conda environment after opening the repository

```bash
conda create -p venv python=3.8 -y
```

```bash
conda activate venv/
```

### Step 3 - Install the requirements
```bash
pip install -r requirements.txt
```

### Step 4 - Get AWS credentials
```bash
Get the Training artifact Bucket name from Model trainer https://github.com/bsb4018/bsb_rec_sys_mti.git
Goto src/constants/cloud_constants.py and replace the name S3_TRAINING_BUCKET_NAME accordingly

Get a note of the following
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION_NAME
```

### Step 5 - Get Mongo DB credentials
```bash
Get the Mongo DB Collections Name from Data Store https://github.com/bsb4018/bsb_rec_sys_data_store.git
Goto src/constants/cloud_constants.py and replace the names accordingly

Get a note of the following
MONGO_DB_URL
```


### Step 6 - Export the environment variable
```bash
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>

export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>

export AWS_REGION_NAME=<AWS_REGION_NAME>

export MONGODB_URL_KEY =<MONGO_DB_URL>
```


### Step 7 - Run locally
```bash
python app.py
```


## Runing Through Docker

1. Check if the Dockerfile is available in the project directory

2. Build the Docker image
```
docker build --build-arg AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> --build-arg AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> --build-arg AWS_REGION_NAME=<AWS_REGION_NAME> --build-arg MONGO_DB_URL_KEY=<MONGO_DB_URL> . 

```

3. Run the Docker image
```
docker run -d -p 8090:8090 <IMAGE_NAME>
```
