from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    TargetDriftPreset,
    DataQualityPreset,
)
from evidently import ColumnMapping


import requests
import pandas as pd


class ModelMonitoringHandler:
    def __init__(self, disc_service_url: str, target: str):
        self.disc_service = disc_service_url
        self.target = target

    def _gather_data(self):
        service_info = requests.get(f"{self.disc_service}/discover/dataservice").json()
        dataservice_ip = service_info.get("name")
        dataservice_port = service_info.get("port")

        dataservice_url = (
            f"http://{dataservice_ip}:{dataservice_port}/api/v1/{self.target}/full"
        )

        r = requests.get(dataservice_url)
        response_data = r.json()
        data = response_data["data"]
        latest_date = response_data["latestDate"]

        service_info = requests.get(f"{self.disc_service}/discover/trainservice").json()
        trainservice_ip = service_info.get("name")
        trainservice_port = service_info.get("port")

        train_service = (
            f"http://{trainservice_ip}:{trainservice_port}/api/v1/trainingdate"
        )

        r = requests.get(train_service).text

        df = pd.DataFrame(data)
        reference = df[df["ds"] == r]
        current = df[df["ds"] > r]

        return current, reference

    def build_report(self):
        current, reference = self._gather_data()
        column_mapping = ColumnMapping()
        drift_report = Report(metrics=[DataDriftPreset()])

        drift_report.run(reference_data=reference, current_data=current)
        drift_report.save_html("./templates/index.html")
