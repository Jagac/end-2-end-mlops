import os
from dataclasses import dataclass

import mlflow


@dataclass
class Config:
    aws_default_region: str = "eu-west-3"
    aws_region: str = "eu-west-3"
    aws_access_key_id: str = "admin"
    aws_secret_access_key: str = "adminadmin"
    mlflow_s3_endpoint_url: str = "http://minio:9000"
    mlflow_tracking_uri: str = "http://mlflow-server:5000"

    def setup_environment(self):
        os.environ["AWS_DEFAULT_REGION"] = self.aws_default_region
        os.environ["AWS_REGION"] = self.aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = self.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.aws_secret_access_key
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = self.mlflow_s3_endpoint_url
        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        print("Env set up")
