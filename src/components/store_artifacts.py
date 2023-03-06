from src.configurations.aws_config import AwsStorage
from boto3 import Session
import os,sys
from src.logger import logging
from src.exception import PredictionException
from src.constants.file_constants import PRODUCTION_MODEL_FILE_PATH
from memory_profiler import profile
class StorageConnection:
    """
    Created connection with S3 bucket using boto3 api to fetch the model from Repository.
    """
    def __init__(self):
        try:
            logging.info("Getting AWS Configurations")
            self.config = AwsStorage()
            self.session = Session(aws_access_key_id=self.config.ACCESS_KEY_ID,
                                   aws_secret_access_key=self.config.SECRET_KEY,
                                   region_name=self.config.REGION_NAME)
            self.s3 = self.session.resource("s3")
            self.bucket = self.s3.Bucket(self.config.BUCKET_NAME)
            logging.info("AWS Configured and Session Set")

        except Exception as e:
            raise PredictionException(e,sys)

    @profile
    def download_production_model_s3(self):
        """
        Download the contents of a folder directory
        Args:
            bucket_name: the name of the s3 bucket
            s3_folder: the folder path in the s3 bucket
            local_dir: a relative or absolute directory path in the local file system
        """
        try:
            logging.info("Connecting to Bucket -> Starting Download")
            s3_folder = "saved_models"
            local_dir = PRODUCTION_MODEL_FILE_PATH
            bucket = self.bucket
            for obj in bucket.objects.filter(Prefix=s3_folder):
                target = obj.key if local_dir is None \
                    else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
                if not os.path.exists(os.path.dirname(target)):
                    os.makedirs(os.path.dirname(target))
                if obj.key[-1] == '/':
                    continue
                bucket.download_file(obj.key, target)

            logging.info("Download Complete")

        except Exception as e:
            raise PredictionException(e,sys)
    


if __name__ == "__main__":
    #Dummy Main Function to Test Use
    connection = StorageConnection()
    #connection.download_production_model_s3()

