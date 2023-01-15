import os
from from_root import from_root
from src.constants.cloud_constants import AWS_ACCESS_KEY_ID_ENV_KEY,AWS_REGION_NAME,AWS_SECRET_ACCESS_KEY_ENV_KEY,S3_TRAINING_BUCKET_NAME
class AwsStorage:
    def __init__(self):
        self.ACCESS_KEY_ID = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY)
        self.SECRET_KEY = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY)
        self.REGION_NAME = os.getenv(AWS_REGION_NAME)
        self.BUCKET_NAME = S3_TRAINING_BUCKET_NAME

    def get_aws_storage_config(self):
        return self.__dict__