from abc import ABC, abstractmethod

import pandas as pd
import yaml
from celery import Celery

from .modelhandler import ModelRegistryHandler
from .params import global_variables


class HandleTask(ABC):
    @abstractmethod
    def fuel_task(self) -> None:
        pass


class TaskFactory(HandleTask):
    def fuel_task(self, fuel_type) -> Celery:
        if fuel_type == "euro95":
            return Euro95Task().fuel_task()
        elif fuel_type == "diesel":
            return DieselTask().fuel_task()
        elif fuel_type == "lpg":
            return LpgTask().fuel_task()
        else:
            raise ValueError("Invalid fuel type")


class Euro95Task(HandleTask):
    def __init__(self) -> None:
        self.euro_celery = Celery(
            "euro95_preds",
            broker="redis://localhost:6379",
            backend="redis://localhost:6379",
        )

    def fuel_task(self) -> Celery:
        floor = global_variables["euro95"]["floor"]
        cap = global_variables["euro95"]["cap"]
        reg = ModelRegistryHandler("euro95_1-2024-03-04")
        model = reg.load_model(model_version=1)

        @self.euro_celery.task(queue="eu95_queue")
        def predict_eu95(data):
            dates_to_predict = data.get("dates")

            if dates_to_predict is None:
                return {"error": "No dates provided for prediction"}

            results = []
            for date_to_predict in dates_to_predict:
                future = pd.DataFrame(
                    {"ds": [date_to_predict], "floor": floor, "cap": cap}
                )
                forecast = model.predict(future)
                result = {
                    "ds": forecast["ds"].iloc[0],
                    "yhat": forecast["yhat"].iloc[0],
                }
                results.append(result)

            return {"results": results}

        return predict_eu95


class DieselTask(HandleTask):
    def __init__(self) -> None:
        self.diesel_celery = Celery(
            "disel_preds",
            broker="redis://localhost:6379",
            backend="redis://localhost:6379",
        )

    def fuel_task(self) -> Celery:
        floor = global_variables["diesel"]["floor"]
        cap = global_variables["diesel"]["cap"]
        reg = ModelRegistryHandler("diesel_2-2024-03-04")
        model = reg.load_model(model_version=1)

        @self.diesel_celery.task(queue="diesel_queue")
        def predict_diesel(data):
            dates_to_predict = data.get("dates")

            if dates_to_predict is None:
                return {"error": "No dates provided for prediction"}

            results = []
            for date_to_predict in dates_to_predict:
                future = pd.DataFrame(
                    {"ds": [date_to_predict], "floor": floor, "cap": cap}
                )
                forecast = model.predict(future)
                result = {
                    "ds": forecast["ds"].iloc[0],
                    "yhat": forecast["yhat"].iloc[0],
                }
                results.append(result)

            return {"results": results}

        return predict_diesel


class LpgTask(HandleTask):
    def __init__(self):
        self.lpg_celery = Celery(
            "lpg_preds",
            broker="redis://redis:6379",
            backend="redis://redis:6379",
        )

    def fuel_task(self) -> Celery:
        floor = global_variables["lpg"]["floor"]
        cap = global_variables["lpg"]["cap"]
        reg = ModelRegistryHandler("lpg_3-2024-03-04")
        model = reg.load_model(model_version=1)

        @self.lpg_celery.task(queue="lpg_queue")
        def predict_lpg(data):
            dates_to_predict = data.get("dates")

            if dates_to_predict is None:
                return {"error": "No dates provided for prediction"}

            results = []
            for date_to_predict in dates_to_predict:
                future = pd.DataFrame(
                    {"ds": [date_to_predict], "floor": floor, "cap": cap}
                )
                forecast = model.predict(future)
                result = {
                    "ds": forecast["ds"].iloc[0],
                    "yhat": forecast["yhat"].iloc[0],
                }
                results.append(result)

            return {"results": results}

        return predict_lpg
