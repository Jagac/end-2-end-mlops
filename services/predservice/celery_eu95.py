import pandas as pd
from celery import Celery
from fp import RegistryHandler
import yaml

with open("config.yaml", "r") as file:
    global_variables = yaml.safe_load(file)

floor = global_variables["euro95"]["floor"]
cap = global_variables["euro95"]["cap"]

reg = RegistryHandler("euro95_1-2024-01-28")
model = reg.load_model(model_version=1)


euro_celery = Celery(
    "euro95_preds", broker="redis://localhost:6379", backend="redis://localhost:6379"
)


@euro_celery.task(queue="eu95_queue")
def predict_eu95(data):
    dates_to_predict = data.get("dates")

    if dates_to_predict is None:
        return {"error": "No dates provided for prediction"}

    results = []
    for date_to_predict in dates_to_predict:
        future = pd.DataFrame({"ds": [date_to_predict], "floor": floor, "cap": cap})
        forecast = model.predict(future)
        result = {"ds": forecast["ds"].iloc[0], "yhat": forecast["yhat"].iloc[0]}
        results.append(result)

    return {"results": results}
