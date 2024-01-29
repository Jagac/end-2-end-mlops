from typing import Optional

import mlflow
import mlflow.prophet
from mlflow import MlflowClient

from .config import Config


class RegistryHandler:
    def __init__(
        self, model_name: str, client: Optional[MlflowClient] = MlflowClient()
    ) -> None:
        self.model_name = model_name
        self.client = client
        self.config = Config()
        self.config.setup_environment()

    def load_model(self, model_version: int):
        model = mlflow.prophet.load_model(
            model_uri=f"models:/{self.model_name}/{model_version}"
        )
        return model

    def transition_model_stage(self, version: int, stage: str) -> None:
        self.client.transition_model_version_stage(
            name=f"{self.model_name}", version=version, stage=f"{stage}"
        )

    def get_model_info(self, stage: str) -> None:
        for mv in self.client.search_model_versions(f"name='{self.model_name}'"):
            info = dict(mv)
            if info["current_stage"] == f"{stage}":
                print(f"[MODEL INFO] : {info}")
